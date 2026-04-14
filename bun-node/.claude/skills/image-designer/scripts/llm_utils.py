#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
llm_utils.py
LLM 调用工具模块 - 提供统一的超时、重试和错误处理机制

功能：
- 统一的 Qwen 客户端初始化（带超时配置）
- 带指数退避的重试机制
- 错误分类处理（超时、连接错误、API 限流等）
- 进度提示和日志记录
"""

import os
import io
import sys
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from openai import OpenAI, APITimeoutError, APIConnectionError, APIError
import dashscope

# 设置 UTF-8 编码（解决 Windows 中文乱码问题）
# 使用安全的方式，避免 "I/O operation on closed file" 错误
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
except (AttributeError, io.UnsupportedOperation, ValueError):
    pass  # 如果 reconfigure 失败，使用默认编码

# ==================== 常量定义 ====================

# 默认超时配置（秒）
DEFAULT_TIMEOUT = 180.0  # 文本回答默认 3 分钟超时
IMAGE_GENERATION_TIMEOUT = 300.0  # 图片生成默认 5 分钟超时
REQUESTS_TIMEOUT = 60.0  # HTTP 请求超时

# 重试配置
MAX_RETRIES = 3  # 最大重试次数
RETRY_BASE_DELAY = 2.0  # 基础重试延迟（秒）
RETRY_MAX_DELAY = 30.0  # 最大重试延迟（秒）

# API 配置
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 异步并发配置（全局默认最大并发任务数）
MAX_CONCURRENT_TASKS = 5  # 图片分析/设计计划/图片生成等异步任务的最大并发数


# ==================== 客户端初始化 ====================

def initialize_qwen_client(timeout: float = DEFAULT_TIMEOUT) -> OpenAI:
    """
    初始化 Qwen 客户端（文本生成）

    Args:
        timeout: 超时时间（秒），默认 180 秒

    Returns:
        OpenAI: 配置好的客户端实例
    """
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("环境变量 DASHSCOPE_API_KEY 未设置，请检查 .env 配置")

    return OpenAI(
        api_key=api_key,
        base_url=DASHSCOPE_BASE_URL,
        timeout=timeout
    )


def initialize_dashscope_client() -> str:
    """
    初始化 DashScope 客户端（图片生成）

    Returns:
        str: API key
    """
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("环境变量 DASHSCOPE_API_KEY 未设置，请检查 .env 配置")

    dashscope.api_key = api_key
    return api_key


# ==================== 重试装饰器 ====================

def retry_with_backoff(max_retries: int = MAX_RETRIES,
                       base_delay: float = RETRY_BASE_DELAY,
                       max_delay: float = RETRY_MAX_DELAY,
                       progress_prefix: str = ""):
    """
    带指数退避的重试装饰器

    Args:
        max_retries: 最大重试次数
        base_delay: 基础延迟时间（秒）
        max_delay: 最大延迟时间（秒）
        progress_prefix: 进度提示前缀

    Returns:
        装饰器函数
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except APITimeoutError as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        _print_progress(f"{progress_prefix}请求超时，{attempt + 1}/{max_retries}，{delay} 秒后重试...")
                        time.sleep(delay)
                    else:
                        raise LLMRetryError(f"超时重试 {max_retries} 次后仍失败：{e}")

                except APIConnectionError as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        _print_progress(f"{progress_prefix}连接错误，{attempt + 1}/{max_retries}，{delay} 秒后重试...")
                        time.sleep(delay)
                    else:
                        raise LLMRetryError(f"连接重试 {max_retries} 次后仍失败：{e}")

                except APIError as e:
                    # API 错误，检查是否是限流
                    error_msg = str(e).lower()
                    if e.status_code == 429 or "rate limit" in error_msg or "too many requests" in error_msg:
                        last_exception = e
                        if attempt < max_retries:
                            # 限流时使用更长的等待时间
                            delay = min(base_delay * (2 ** (attempt + 2)), max_delay * 2)
                            _print_progress(f"{progress_prefix}API 限流 (429)，{attempt + 1}/{max_retries}，{delay} 秒后重试...")
                            time.sleep(delay)
                        else:
                            raise LLMRetryError(f"限流重试 {max_retries} 次后仍失败：{e}")
                    else:
                        # 其他 API 错误，不重试
                        raise LLMAPIError(f"API 错误 ({e.status_code}): {e}")

                except Exception as e:
                    # 其他未知错误
                    error_msg = str(e).lower()
                    # 检查是否可能是网络相关错误
                    if any(keyword in error_msg for keyword in ["connection", "timeout", "network", "socket", "http"]):
                        last_exception = e
                        if attempt < max_retries:
                            delay = min(base_delay * (2 ** attempt), max_delay)
                            _print_progress(f"{progress_prefix}网络错误，{attempt + 1}/{max_retries}，{delay} 秒后重试...")
                            time.sleep(delay)
                        else:
                            raise LLMRetryError(f"网络错误重试 {max_retries} 次后仍失败：{e}")
                    else:
                        # 非网络错误，直接抛出
                        raise

            # 理论上不会到这里
            raise LLMRetryError(f"未知错误，重试后仍失败：{last_exception}")

        wrapper.__name__ = func.__name__
        return wrapper
    return decorator


# ==================== 自定义异常类 ====================

class LLMError(Exception):
    """LLM 调用基础异常"""
    pass


class LLMTimeoutError(LLMError):
    """LLM 调用超时异常"""
    pass


class LLMConnectionError(LLMError):
    """LLM 连接错误异常"""
    pass


class LLMRateLimitError(LLMError):
    """LLM API 限流异常"""
    pass


class LLMRetryError(LLMError):
    """LLM 重试失败异常"""
    pass


class LLMAPIError(LLMError):
    """LLM API 错误异常"""
    pass


# ==================== 辅助函数 ====================

def _print_progress(message: str):
    """打印进度信息"""
    print(message, file=sys.stderr)


def check_api_key() -> bool:
    """
    检查 API Key 是否配置

    Returns:
        bool: 是否已配置
    """
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("错误：环境变量 DASHSCOPE_API_KEY 未设置", file=sys.stderr)
        print("请设置环境变量或创建 .env 文件", file=sys.stderr)
        return False
    return True


def format_error_message(error: Exception, context: str = "") -> str:
    """
    格式化错误消息

    Args:
        error: 异常对象
        context: 上下文信息

    Returns:
        str: 格式化后的错误消息
    """
    error_type = type(error).__name__
    error_msg = str(error)

    if context:
        return f"[{context}] {error_type}: {error_msg}"
    return f"{error_type}: {error_msg}"


# ==================== 文本回答生成（带重试） ====================

@retry_with_backoff(progress_prefix="[LLM] ")
def generate_text_response(client: OpenAI,
                           model: str,
                           messages: List[Dict[str, str]],
                           temperature: float = 0.7,
                           max_tokens: Optional[int] = None,
                           progress_prefix: str = "") -> str:
    """
    生成文本响应（带重试机制）

    Args:
        client: OpenAI 客户端实例
        model: 模型名称
        messages: 消息列表
        temperature: 温度参数
        max_tokens: 最大 token 数
        progress_prefix: 进度提示前缀

    Returns:
        str: 生成的文本内容
    """
    _print_progress(f"{progress_prefix}正在调用 {model} 模型...")

    kwargs = {
        "model": model,
        "messages": messages,
        "temperature": temperature
    }

    if max_tokens:
        kwargs["max_tokens"] = max_tokens

    response = client.chat.completions.create(**kwargs)

    if not response.choices or len(response.choices) == 0:
        raise LLMError("API 返回空响应")

    content = response.choices[0].message.content

    if not content:
        raise LLMError("API 返回空内容")

    _print_progress(f"{progress_prefix}响应生成完成")
    return content


def generate_text_with_messages(messages: List[Dict[str, str]],
                                 model: str = "qwen-max-latest",
                                 temperature: float = 0.7,
                                 max_tokens: Optional[int] = None,
                                 progress_prefix: str = "") -> str:
    """
    生成文本响应（简化版，脚本只需提供 messages）

    Args:
        messages: 消息列表
        model: 模型名称，默认 qwen-max-latest
        temperature: 温度参数，默认 0.7
        max_tokens: 最大 token 数
        progress_prefix: 进度提示前缀

    Returns:
        str: 生成的文本内容
    """
    client = initialize_qwen_client(timeout=180.0)

    return generate_text_response(
        client=client,
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        progress_prefix=progress_prefix
    )


# ==================== 图片生成辅助函数 ====================

def download_image_with_retry(image_url: str,
                              save_path: Path,
                              timeout: float = REQUESTS_TIMEOUT,
                              max_retries: int = 3) -> Path:
    """
    下载图片（带重试机制）

    Args:
        image_url: 图片 URL
        save_path: 保存路径
        timeout: HTTP 请求超时
        max_retries: 最大重试次数

    Returns:
        Path: 保存的图片路径
    """
    import requests

    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(image_url, headers=headers, timeout=timeout)
            response.raise_for_status()

            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'wb') as f:
                f.write(response.content)

            return save_path

        except requests.exceptions.Timeout as e:
            last_exception = e
            if attempt < max_retries:
                delay = RETRY_BASE_DELAY * (2 ** attempt)
                _print_progress(f"[图片下载] 超时，{attempt + 1}/{max_retries}，{delay} 秒后重试...")
                time.sleep(delay)

        except requests.exceptions.ConnectionError as e:
            last_exception = e
            if attempt < max_retries:
                delay = RETRY_BASE_DELAY * (2 ** attempt)
                _print_progress(f"[图片下载] 连接错误，{attempt + 1}/{max_retries}，{delay} 秒后重试...")
                time.sleep(delay)

        except requests.exceptions.HTTPError as e:
            last_exception = e
            if attempt < max_retries:
                delay = RETRY_BASE_DELAY * (2 ** attempt)
                _print_progress(f"[图片下载] HTTP 错误，{attempt + 1}/{max_retries}，{delay} 秒后重试...")
                time.sleep(delay)

        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                delay = RETRY_BASE_DELAY * (2 ** attempt)
                _print_progress(f"[图片下载] 错误，{attempt + 1}/{max_retries}，{delay} 秒后重试...")
                time.sleep(delay)
            else:
                raise

    raise LLMRetryError(f"图片下载重试 {max_retries} 次后仍失败：{last_exception}")


# ==================== 图片生成（带重试） ====================

def generate_image_with_dashscope(prompt: str,
                                  image_index: int = 1,
                                  model: str = "wan2.5-t2i-preview",
                                  progress_prefix: str = "",
                                  save_dir: Optional[Path] = None) -> str:
    """
    使用 DashScope 通义万相生成图片（带重试机制）

    Args:
        prompt: 图片生成 prompt
        image_index: 图片编号
        model: 模型名称，默认 wan2.5-t2i-preview
        progress_prefix: 进度提示前缀
        save_dir: 保存目录，默认使用当前项目的 output 文件夹

    Returns:
        str: 生成的图片保存路径
    """
    import requests
    from http import HTTPStatus

    # 初始化 DashScope
    initialize_dashscope_client()

    last_exception = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            # 调用通义万相 API
            _print_progress(f"{progress_prefix}正在调用通义万相 API...")
            rsp = dashscope.ImageSynthesis.call(
                model=model,
                prompt=prompt,
                n=1
            )

            if rsp.status_code != HTTPStatus.OK:
                raise Exception(f"API 调用失败：{rsp.code} - {rsp.message}")

            if not rsp.output or 'results' not in rsp.output or len(rsp.output['results']) == 0:
                raise Exception(f"未获取到图片：{rsp}")

            # 获取生成的图片 URL
            image_url = rsp.output['results'][0]['url']

            # 确定保存路径
            if save_dir is None:
                save_dir = Path.cwd() / "output"
            save_dir.mkdir(exist_ok=True)
            image_path = save_dir / f"generated_image_{image_index}.png"

            # 下载图片
            _print_progress(f"{progress_prefix}正在下载图片...")
            download_image_with_retry(image_url, image_path)

            return str(image_path)

        except Exception as e:
            last_exception = e
            error_msg = str(e).lower()

            # 超时错误
            if "timeout" in error_msg or "timed out" in error_msg:
                if attempt < MAX_RETRIES:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    _print_progress(f"{progress_prefix}超时，{attempt + 1}/{MAX_RETRIES}，{delay} 秒后重试...")
                    time.sleep(delay)
                else:
                    _print_progress(f"{progress_prefix}超时重试 {MAX_RETRIES} 次后仍失败")

            # 连接错误
            elif "connection" in error_msg or "network" in error_msg:
                if attempt < MAX_RETRIES:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    _print_progress(f"{progress_prefix}连接错误，{attempt + 1}/{MAX_RETRIES}，{delay} 秒后重试...")
                    time.sleep(delay)
                else:
                    _print_progress(f"{progress_prefix}连接重试 {MAX_RETRIES} 次后仍失败")

            # API 限流
            elif "429" in error_msg or "rate limit" in error_msg:
                if attempt < MAX_RETRIES:
                    delay = RETRY_BASE_DELAY * (2 ** (attempt + 2))
                    _print_progress(f"{progress_prefix}API 限流 (429)，{attempt + 1}/{MAX_RETRIES}，{delay} 秒后重试...")
                    time.sleep(delay)
                else:
                    _print_progress(f"{progress_prefix}限流重试 {MAX_RETRIES} 次后仍失败")

            # 其他错误
            else:
                if attempt < MAX_RETRIES:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    _print_progress(f"{progress_prefix}错误：{e}，{attempt + 1}/{MAX_RETRIES}，{delay} 秒后重试...")
                    time.sleep(delay)
                else:
                    _print_progress(f"{progress_prefix}重试 {MAX_RETRIES} 次后仍失败")

    # 所有重试失败，创建错误记录文件
    if save_dir is None:
        save_dir = Path.cwd() / "output"
    save_dir.mkdir(exist_ok=True)
    placeholder_path = save_dir / f"generated_image_{image_index}_failed.txt"

    with open(placeholder_path, 'w', encoding='utf-8') as f:
        f.write(f"图片生成失败\n")
        f.write(f"错误：{str(last_exception)}\n")

    return str(placeholder_path)


# ==================== 图片编辑（图生图，带重试） ====================

def edit_image_with_dashscope(image_path: str,
                              edit_prompt: str,
                              model: str = "wan2.5-i2i-preview",
                              progress_prefix: str = "") -> Optional[str]:
    """
    使用 DashScope 通义万相图生图模型编辑图片（带重试机制）

    Args:
        image_path: 原图路径
        edit_prompt: 修改要求
        model: 模型名称，默认 wan2.5-i2i-preview
        progress_prefix: 进度提示前缀

    Returns:
        str: 生成的图片 URL，失败返回 None
    """
    import requests
    from http import HTTPStatus

    # 初始化 DashScope
    initialize_dashscope_client()

    # 使用本地文件路径调用 API
    _print_progress(f"{progress_prefix}正在调用 {model} 模型进行图片编辑...")

    last_exception = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            # 通义万相图生图 API 参数：
            # model: 模型名称
            # prompt: 提示词
            # images: 图片 URL 列表（支持本地文件路径）
            rsp = dashscope.ImageSynthesis.call(
                model=model,
                prompt=edit_prompt,
                images=["file://" + image_path]
            )

            if rsp.status_code != HTTPStatus.OK:
                raise Exception(f"API 调用失败：{rsp.code} - {rsp.message}")

            if not rsp.output or 'results' not in rsp.output or len(rsp.output['results']) == 0:
                raise Exception(f"未获取到图片：{rsp}")

            # 获取生成的图片 URL
            image_url = rsp.output['results'][0]['url']
            _print_progress(f"{progress_prefix}图片生成成功")
            return image_url

        except Exception as e:
            last_exception = e
            error_msg = str(e).lower()

            # 超时错误
            if "timeout" in error_msg or "timed out" in error_msg:
                if attempt < MAX_RETRIES:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    _print_progress(f"{progress_prefix}超时，{attempt + 1}/{MAX_RETRIES}，{delay} 秒后重试...")
                    time.sleep(delay)
                else:
                    _print_progress(f"{progress_prefix}超时重试 {MAX_RETRIES} 次后仍失败")

            # 连接错误
            elif "connection" in error_msg or "network" in error_msg:
                if attempt < MAX_RETRIES:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    _print_progress(f"{progress_prefix}连接错误，{attempt + 1}/{MAX_RETRIES}，{delay} 秒后重试...")
                    time.sleep(delay)
                else:
                    _print_progress(f"{progress_prefix}连接重试 {MAX_RETRIES} 次后仍失败")

            # API 限流
            elif "429" in error_msg or "rate limit" in error_msg:
                if attempt < MAX_RETRIES:
                    delay = RETRY_BASE_DELAY * (2 ** (attempt + 2))
                    _print_progress(f"{progress_prefix}API 限流 (429)，{attempt + 1}/{MAX_RETRIES}，{delay} 秒后重试...")
                    time.sleep(delay)
                else:
                    _print_progress(f"{progress_prefix}限流重试 {MAX_RETRIES} 次后仍失败")

            # 其他错误
            else:
                if attempt < MAX_RETRIES:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    _print_progress(f"{progress_prefix}错误：{e}，{attempt + 1}/{MAX_RETRIES}，{delay} 秒后重试...")
                    time.sleep(delay)
                else:
                    _print_progress(f"{progress_prefix}重试 {MAX_RETRIES} 次后仍失败")

    # 所有重试失败
    _print_progress(f"{progress_prefix}图片编辑失败：{str(last_exception)}")
    return None


# ==================== 视觉模型分析（使用 DashScope 原生 SDK） ====================

def analyze_image_with_qwen_vl(image_path: str,
                                user_prompt: str,
                                system_prompt: str = "你是一个专业的图片分析专家。",
                                model: str = "qwen-vl-max-latest",
                                progress_prefix: str = "") -> str:
    """
    使用 Qwen 视觉模型分析图片（带重试机制）
    使用 DashScope 原生 SDK 支持本地文件路径

    Args:
        image_path: 图片路径
        user_prompt: 用户提示文字
        system_prompt: 系统提示，默认"你是一个专业的图片分析专家。"
        model: 模型名称，默认 qwen-vl-max-latest
        progress_prefix: 进度提示前缀

    Returns:
        str: 图片分析结果
    """
    from dashscope import MultiModalConversation
    from http import HTTPStatus

    # 初始化 DashScope
    initialize_dashscope_client()

    last_exception = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            _print_progress(f"{progress_prefix}正在分析图片...")

            # 使用 DashScope 原生 SDK 的 MultiModalConversation 接口
            # 直接传入本地文件路径，SDK 会自动处理
            response = MultiModalConversation.call(
                model=model,
                messages=[
                    {
                        'role': 'system',
                        'content': [{'text': system_prompt}]
                    },
                    {
                        'role': 'user',
                        'content': [
                            {'image': image_path},  # 直接传入本地文件路径
                            {'text': user_prompt}
                        ]
                    }
                ]
            )

            if response.status_code != HTTPStatus.OK:
                raise Exception(f"API 调用失败：{response.code} - {response.message}")

            if not response.output or 'choices' not in response.output:
                return "[图片分析失败：API 返回空响应]"

            content = response.output['choices'][0]['message']['content'][0]['text']
            _print_progress(f"{progress_prefix}图片分析完成")
            return content if content else "[图片分析失败：API 返回空内容]"

        except FileNotFoundError as e:
            return f"[图片分析失败：{str(e)}]"

        except Exception as e:
            last_exception = e
            error_msg = str(e).lower()

            if "timeout" in error_msg or "timed out" in error_msg:
                if attempt < MAX_RETRIES:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    _print_progress(f"{progress_prefix}超时，{attempt + 1}/{MAX_RETRIES}，{delay} 秒后重试...")
                    time.sleep(delay)
                else:
                    _print_progress(f"{progress_prefix}超时重试 {MAX_RETRIES} 次后仍失败")

            elif "connection" in error_msg or "network" in error_msg:
                if attempt < MAX_RETRIES:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    _print_progress(f"{progress_prefix}连接错误，{attempt + 1}/{MAX_RETRIES}，{delay} 秒后重试...")
                    time.sleep(delay)
                else:
                    _print_progress(f"{progress_prefix}连接重试 {MAX_RETRIES} 次后仍失败")

            elif "429" in error_msg or "rate limit" in error_msg:
                if attempt < MAX_RETRIES:
                    delay = RETRY_BASE_DELAY * (2 ** (attempt + 2))
                    _print_progress(f"{progress_prefix}API 限流 (429)，{attempt + 1}/{MAX_RETRIES}，{delay} 秒后重试...")
                    time.sleep(delay)
                else:
                    _print_progress(f"{progress_prefix}限流重试 {MAX_RETRIES} 次后仍失败")

            else:
                if attempt < MAX_RETRIES:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    _print_progress(f"{progress_prefix}错误：{e}，{attempt + 1}/{MAX_RETRIES}，{delay} 秒后重试...")
                    time.sleep(delay)
                else:
                    _print_progress(f"{progress_prefix}重试 {MAX_RETRIES} 次后仍失败")

    return f"[图片分析失败：{str(last_exception)}]"


# ==================== 翻译文本函数（带重试） ====================
def translate_text(text: str,
                   target_language: str = "English",
                   progress_prefix: str = "") -> str:
    """
    翻译文本（使用 Qwen 模型）

    Args:
        text: 待翻译的文本
        target_language: 目标语言，默认 English
        progress_prefix: 进度提示前缀

    Returns:
        str: 翻译后的文本
    """
    messages = [
        {"role": "system", "content": f"将设计相关的词汇翻译为{target_language}，只返回翻译结果，不要任何解释。"},
        {"role": "user", "content": text}
    ]

    try:
        result = generate_text_with_messages(
            messages=messages,
            model="qwen-max-latest",
            temperature=0.3,
            progress_prefix=progress_prefix
        )
        return result.strip()
    except Exception as e:
        print(f"[翻译失败] {e}")
        return text  # 翻译失败返回原文

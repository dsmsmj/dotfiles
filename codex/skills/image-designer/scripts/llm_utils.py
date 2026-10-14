#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
llm_utils.py
LLM 调用工具模块 - 提供统一的超时、重试和错误处理机制

功能：
- MiniMax 文本（OpenAI 兼容）与原生多模态视觉接口
- 文生图 / 图生图（/v1/image_generation）
- 带指数退避的重试机制
"""

import base64
import io
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv
from openai import APIConnectionError, APIError, APITimeoutError, OpenAI

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
except (AttributeError, io.UnsupportedOperation, ValueError):
    pass

load_dotenv(Path(__file__).parent.parent / ".env")

DEFAULT_TIMEOUT = 180.0
IMAGE_GENERATION_TIMEOUT = 300.0
REQUESTS_TIMEOUT = 60.0

MAX_RETRIES = 3
RETRY_BASE_DELAY = 2.0
RETRY_MAX_DELAY = 30.0

MAX_CONCURRENT_TASKS = 5

DEFAULT_MINIMAX_BASE_URL = 'https://api.minimax.io/v1'


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

def get_minimax_api_key() -> str:
    key = os.getenv('MINIMAX_API_KEY')
    if not key:
        raise ValueError('环境变量 MINIMAX_API_KEY 未设置，请检查 .env 配置')
    return key


def get_minimax_api_origin() -> str:
    raw = os.getenv('MINIMAX_BASE_URL', DEFAULT_MINIMAX_BASE_URL).strip().rstrip('/')
    if raw.endswith('/v1'):
        return raw[:-3]
    return raw


def get_minimax_text_model() -> str:
    return os.getenv('MINIMAX_TEXT_MODEL', 'MiniMax-M2.5')


def get_minimax_vision_model() -> str:
    return os.getenv('MINIMAX_VISION_MODEL', 'MiniMax-Text-01')


def get_minimax_t2i_model() -> str:
    return os.getenv('MINIMAX_T2I_MODEL', 'image-01')


def get_minimax_i2i_model() -> str:
    return os.getenv('MINIMAX_I2I_MODEL', 'image-01')


def initialize_minimax_openai_client(timeout: float = DEFAULT_TIMEOUT) -> OpenAI:
    base = os.getenv('MINIMAX_BASE_URL', DEFAULT_MINIMAX_BASE_URL).strip().rstrip('/')
    return OpenAI(
        api_key=get_minimax_api_key(),
        base_url=base,
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Error hierarchy
# ---------------------------------------------------------------------------

class LLMError(Exception):
    pass


class LLMTimeoutError(LLMError):
    pass


class LLMConnectionError(LLMError):
    pass


class LLMRateLimitError(LLMError):
    pass


class LLMRetryError(LLMError):
    pass


class LLMAPIError(LLMError):
    pass


# ---------------------------------------------------------------------------
# Logging / checks
# ---------------------------------------------------------------------------

def _print_progress(message: str):
    print(message, file=sys.stderr)


def check_api_key() -> bool:
    if not os.getenv('MINIMAX_API_KEY'):
        print('错误：环境变量 MINIMAX_API_KEY 未设置', file=sys.stderr)
        print('请设置环境变量或创建 .env 文件', file=sys.stderr)
        return False
    return True


def format_error_message(error: Exception, context: str = '') -> str:
    error_type = type(error).__name__
    error_msg = str(error)
    if context:
        return f'[{context}] {error_type}: {error_msg}'
    return f'{error_type}: {error_msg}'


# ---------------------------------------------------------------------------
# Unified retry decorator – handles openai + requests + generic exceptions
# ---------------------------------------------------------------------------

def _is_retryable(exc: Exception) -> bool:
    if isinstance(exc, (APITimeoutError, APIConnectionError)):
        return True
    if isinstance(exc, APIError):
        msg = str(exc).lower()
        return exc.status_code == 429 or 'rate limit' in msg or 'too many requests' in msg
    if isinstance(exc, (requests.exceptions.Timeout, requests.exceptions.ConnectionError)):
        return True
    if isinstance(exc, requests.exceptions.HTTPError):
        return True
    msg = str(exc).lower()
    return any(kw in msg for kw in ('connection', 'timeout', 'network', 'socket', 'http'))


def _retry_delay(attempt: int, exc: Exception) -> float:
    is_rate_limit = (
        (isinstance(exc, APIError) and (exc.status_code == 429 or 'rate limit' in str(exc).lower()))
        or '429' in str(exc)
        or 'rate limit' in str(exc).lower()
    )
    if is_rate_limit:
        return min(RETRY_BASE_DELAY * (2 ** (attempt + 2)), RETRY_MAX_DELAY * 2)
    return min(RETRY_BASE_DELAY * (2 ** attempt), RETRY_MAX_DELAY)


def retry_with_backoff(
    max_retries: int = MAX_RETRIES,
    progress_prefix: str = '',
):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if not _is_retryable(e) and not isinstance(e, (APITimeoutError, APIConnectionError, APIError)):
                        if not _is_retryable(e):
                            raise
                    if attempt >= max_retries:
                        raise LLMRetryError(f'重试 {max_retries} 次后仍失败：{e}')
                    delay = _retry_delay(attempt, e)
                    pfx = kwargs.get('progress_prefix', progress_prefix)
                    _print_progress(f'{pfx}{type(e).__name__}，{attempt + 1}/{max_retries}，{delay:.0f}s 后重试…')
                    time.sleep(delay)
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# Text generation (OpenAI-compatible)
# ---------------------------------------------------------------------------

@retry_with_backoff(progress_prefix='[LLM] ')
def generate_text_response(
    client: OpenAI,
    model: str,
    messages: List[Dict[str, Any]],
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    progress_prefix: str = '',
) -> str:
    _print_progress(f'{progress_prefix}正在调用 {model} 模型...')

    kwargs: Dict[str, Any] = {
        'model': model,
        'messages': messages,
        'temperature': max(0.01, min(temperature, 1.0)),
    }
    if max_tokens:
        kwargs['max_tokens'] = max_tokens

    response = client.chat.completions.create(**kwargs)

    if not response.choices or len(response.choices) == 0:
        raise LLMError('API 返回空响应')
    content = response.choices[0].message.content
    if not content:
        raise LLMError('API 返回空内容')

    _print_progress(f'{progress_prefix}响应生成完成')
    return content


def generate_text_with_messages(
    messages: List[Dict[str, Any]],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    progress_prefix: str = '',
) -> str:
    resolved = model or get_minimax_text_model()
    client = initialize_minimax_openai_client(timeout=180.0)
    return generate_text_response(
        client=client,
        model=resolved,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        progress_prefix=progress_prefix,
    )


# ---------------------------------------------------------------------------
# Image download
# ---------------------------------------------------------------------------

@retry_with_backoff(progress_prefix='[图片下载] ')
def download_image_with_retry(
    image_url: str,
    save_path: Path,
    timeout: float = REQUESTS_TIMEOUT,
) -> Path:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(image_url, headers=headers, timeout=timeout)
    response.raise_for_status()

    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, 'wb') as f:
        f.write(response.content)
    return save_path


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _local_image_to_data_url(image_path: str) -> str:
    p = Path(image_path)
    ext = p.suffix.lower()
    mime_map = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp'}
    mime = mime_map.get(ext, 'image/png')
    b64 = base64.b64encode(p.read_bytes()).decode('ascii')
    return f'data:{mime};base64,{b64}'


def _post_image_generation(body: Dict[str, Any]) -> Dict[str, Any]:
    origin = get_minimax_api_origin()
    url = f'{origin}/v1/image_generation'
    headers = {
        'Authorization': f'Bearer {get_minimax_api_key()}',
        'Content-Type': 'application/json',
    }
    r = requests.post(url, headers=headers, json=body, timeout=IMAGE_GENERATION_TIMEOUT)
    r.raise_for_status()
    return r.json()


def _extract_image_urls(resp: Dict[str, Any]) -> List[str]:
    br = resp.get('base_resp') or {}
    code = br.get('status_code')
    if code != 0:
        raise LLMAPIError(f"图像 API：{br.get('status_msg', resp)}")
    data = resp.get('data') or {}
    return list(data.get('image_urls') or [])


def _post_text_chatcompletion_v2(payload: Dict[str, Any]) -> Dict[str, Any]:
    origin = get_minimax_api_origin()
    url = f'{origin}/v1/text/chatcompletion_v2'
    headers = {
        'Authorization': f'Bearer {get_minimax_api_key()}',
        'Content-Type': 'application/json',
    }
    r = requests.post(url, headers=headers, json=payload, timeout=DEFAULT_TIMEOUT)
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------------------------
# Text-to-Image
# ---------------------------------------------------------------------------

@retry_with_backoff(progress_prefix='[文生图] ')
def generate_image_with_minimax(
    prompt: str,
    image_index: int = 1,
    model: Optional[str] = None,
    progress_prefix: str = '',
    save_dir: Optional[Path] = None,
) -> str:
    resolved_model = model or get_minimax_t2i_model()
    _print_progress(f'{progress_prefix}正在调用 MiniMax 文生图 API...')

    rsp = _post_image_generation({
        'model': resolved_model,
        'prompt': prompt,
        'n': 1,
        'response_format': 'url',
    })
    urls = _extract_image_urls(rsp)
    if not urls:
        raise LLMAPIError(f'未获取到图片：{rsp}')

    if save_dir is None:
        from session_utils import get_session_subdir
        save_dir = get_session_subdir('output')
    save_dir.mkdir(exist_ok=True)
    image_path = save_dir / f'generated_image_{image_index}.png'

    _print_progress(f'{progress_prefix}正在下载图片...')
    download_image_with_retry(urls[0], image_path)
    return str(image_path)


# ---------------------------------------------------------------------------
# Image-to-Image
# ---------------------------------------------------------------------------

@retry_with_backoff(progress_prefix='[图生图] ')
def edit_image_with_minimax(
    image_path: str,
    edit_prompt: str,
    model: Optional[str] = None,
    progress_prefix: str = '',
) -> str:
    resolved_model = model or get_minimax_i2i_model()
    data_url = _local_image_to_data_url(image_path)
    _print_progress(f'{progress_prefix}正在调用 {resolved_model} 进行图生图编辑...')

    rsp = _post_image_generation({
        'model': resolved_model,
        'prompt': edit_prompt,
        'subject_reference': [{'type': 'character', 'image_file': data_url}],
        'n': 1,
        'response_format': 'url',
    })
    urls = _extract_image_urls(rsp)
    if not urls:
        raise LLMAPIError(f'未获取到图片：{rsp}')

    _print_progress(f'{progress_prefix}图片生成成功')
    return urls[0]


# ---------------------------------------------------------------------------
# Vision analysis (native MiniMax endpoint)
# ---------------------------------------------------------------------------

@retry_with_backoff(progress_prefix='[视觉分析] ')
def analyze_image_with_minimax(
    image_path: str,
    user_prompt: str,
    system_prompt: str = '你是一个专业的图片分析专家。',
    model: Optional[str] = None,
    progress_prefix: str = '',
) -> str:
    resolved_model = model or get_minimax_vision_model()
    data_url = _local_image_to_data_url(image_path)
    _print_progress(f'{progress_prefix}正在分析图片...')

    payload = {
        'model': resolved_model,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': user_prompt},
                    {'type': 'image_url', 'image_url': {'url': data_url}},
                ],
            },
        ],
        'temperature': 0.7,
    }

    data = _post_text_chatcompletion_v2(payload)
    br = data.get('base_resp') or {}
    if br.get('status_code') != 0:
        raise LLMAPIError(f"API 调用失败：{br.get('status_msg', data)}")

    choices = data.get('choices') or []
    if not choices:
        return '[图片分析失败：API 返回空响应]'
    msg = choices[0].get('message') or {}
    content = msg.get('content')
    if not content:
        return '[图片分析失败：API 返回空内容]'

    _print_progress(f'{progress_prefix}图片分析完成')
    return content if isinstance(content, str) else str(content)


# ---------------------------------------------------------------------------
# Translation helper
# ---------------------------------------------------------------------------

def translate_text(
    text: str,
    target_language: str = 'English',
    progress_prefix: str = '',
) -> str:
    messages = [
        {
            'role': 'system',
            'content': f'将设计相关的词汇翻译为{target_language}，只返回翻译结果，不要任何解释。',
        },
        {'role': 'user', 'content': text},
    ]
    try:
        result = generate_text_with_messages(
            messages=messages,
            model=get_minimax_text_model(),
            temperature=0.3,
            progress_prefix=progress_prefix,
        )
        return result.strip()
    except Exception as e:
        print(f'[翻译失败] {e}')
        return text

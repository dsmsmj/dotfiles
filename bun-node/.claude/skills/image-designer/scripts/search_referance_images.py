#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
search_referance_images.py
第三步：搜索参考图片脚本

功能：
- 从设计构思中提取关键词（3-5 个）
- 利用关键词通过 Unsplash 和 Pixabay API 搜索图片
- 下载约 20 张图片保存到 reference_images 文件夹

用法:
    python search_referance_images.py "<设计构思文本>"
"""

import sys
import os
import io
import re
import time
from pathlib import Path
import requests

# 设置 UTF-8 编码（解决 Windows 中文乱码问题）
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
except (AttributeError, io.UnsupportedOperation, ValueError):
    pass

# 导入工具模块
from session_utils import get_session_root
from llm_utils import (
    generate_text_with_messages,
    translate_text,
    check_api_key,
    REQUESTS_TIMEOUT
)

# Unsplash API 配置
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")
# Pixabay API 配置
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "")


def get_project_root() -> Path:
    """获取当前 session 的工作根目录（而非项目根目录）"""
    return get_session_root()


def extract_keywords(concept_text: str) -> list:
    """
    从设计构思中提取关键词

    Args:
        concept_text: 设计构思文本

    Returns:
        list: 关键词列表（3-5 个）
    """
    system_prompt = """
你是一位资深视觉设计专家，你拒绝平庸的装饰，主张"设计即解决方案"。你的表达风格：精确、无废话铺垫。擅长内容如下：
1. 品牌与标识设计，包括：Logo 设计，品牌视觉识别系统，名片、信纸等品牌物料。
2. 营销与广告设计，包括：社交媒体海报与横幅，电商产品主图、详情图，促销广告、活动海报，宣传单页、传单。
3. 创意与艺术设计，包括：插画与概念艺术，IP 形象与吉祥物设计，艺术风格化图像，封面设计（书籍、专辑等）。
4. 图像编辑与处理，包括：图片修改与优化，风格转换（如照片转插画），多图合成，背景替换。
5. 内容创作，包括：社交媒体配图，文章/博客封面图，演示文稿视觉素材，节日贺卡。
"""
    prompt = f"""
【任务描述】：
请从设计构思文本中提取 3-5 个最核心的英文关键词，严格执行以下规则：
1. 提取描述色彩、风格、排版、视觉元素、用途、领域等词汇。
2. 关键词倾向于实体名词和具体的场景描述，而非抽象概念。
3. 关键词按重要性从高到低排序，且每个关键词都必须为单个的英文单词（可以带连字符，如 Chinese-style）。
4. 核心名词类关键词（主体）的重要性高于形容词类关键词（氛围、颜色、光影、环境）。
5. 关键词须简洁明确，适合图片搜索。
6. 请只返回关键词列表，关键词与关键词之间用**逗号**分隔，不要其他解释，返回结构必须为：keyword1,keyword2,keyword3。

【示例】：
正确返回：Chinese-style,poster,traditional,ink-painting,lotus
错误返回：Chinese style poster traditional elements（空格分隔，无法区分）
错误返回：Chinese-style poster traditional（超过 1 个单词）

【设计构思】：
{concept_text}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]

    try:
        keywords_text = generate_text_with_messages(
            messages=messages,
            model="qwen-max-latest",
            temperature=0.3,
            progress_prefix="[关键词提取] "
        )

        # 先用逗号分割（新格式），如果不含逗号则用空格分割（兼容旧格式）
        if ',' in keywords_text:
            keywords = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]
        else:
            keywords = [kw.strip() for kw in keywords_text.strip().split(' ') if kw.strip()]

        # 验证和清洗关键词
        validated_keywords = []
        for kw in keywords:
            # 移除前后空白
            kw = kw.strip()
            if not kw:
                continue

            # 检查是否包含空格（如果是，说明 LLM 没有遵守规则，只取第一个单词）
            if ' ' in kw:
                kw = kw.split()[0]

            # 验证关键词格式：只允许字母、数字、连字符
            if not re.match(r'^[a-zA-Z0-9\-]+$', kw):
                # 尝试提取有效的部分
                match = re.search(r'[a-zA-Z][a-zA-Z0-9\-]*', kw)
                if match:
                    kw = match.group()
                else:
                    continue  # 跳过无效关键词

            # 限制关键词长度（避免过长）
            if len(kw) > 30:
                kw = kw[:30]

            validated_keywords.append(kw.lower())

        # 确保是英文关键词
        en_keywords = []
        for kw in validated_keywords:
            # 如果检测到是中文，使用统一翻译函数
            if any('\u4e00' <= char <= '\u9fff' for char in kw):
                en_kw = translate_text(kw, progress_prefix="[翻译] ")
                en_keywords.append(en_kw)
            else:
                en_keywords.append(kw)

        # 去重并保持顺序
        seen = set()
        unique_keywords = []
        for kw in en_keywords:
            kw_lower = kw.lower()
            if kw_lower not in seen:
                seen.add(kw_lower)
                unique_keywords.append(kw)

        return unique_keywords[:5]  # 最多 5 个关键词

    except Exception as e:
        print(f"提取关键词时出错：{e}")
        return ["modern", "design", "minimalist", "creative"]  # 默认关键词


def search_unsplash_images(keywords: list, image_count: int = 5) -> list:
    """
    在 Unsplash 上搜索图片（采用渐进式降级搜索策略）

    Args:
        keywords: 搜索关键词列表 (按重要性从高到低排列)
        image_count: 期望获取的图片总数量，默认为 5

    Returns:
        list: 图片信息字典列表
    """
    if not UNSPLASH_ACCESS_KEY:
        print("警告：未设置 UNSPLASH_ACCESS_KEY 环境变量，使用占位图片")
        return []

    url = "https://api.unsplash.com/search/photos"

    current_keywords = keywords.copy()
    collected_images = {}

    try:
        while len(current_keywords) > 0 and len(collected_images) < image_count:
            current_query = " ".join(current_keywords)

            params = {
                "query": current_query,
                "per_page": max(30, image_count),
                "order_by": "relevant",
                "client_id": UNSPLASH_ACCESS_KEY
            }

            response = requests.get(url, params=params, timeout=REQUESTS_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            for result in data.get("results", []):
                img_id = result["id"]

                if img_id not in collected_images:
                    collected_images[img_id] = {
                        "url": result["urls"]["regular"],
                        "thumbnail": result["urls"]["thumb"],
                        "description": result.get("description", ""),
                        "photographer": result.get("user", {}).get("name", "Unknown")
                    }

                    if len(collected_images) >= image_count:
                        break

            if current_keywords:
                current_keywords.pop()

        return list(collected_images.values())

    except Exception as e:
        query_str = " ".join(current_keywords) if current_keywords else "Empty"
        print(f"搜索 Unsplash 时出错（当前查询组合：{query_str}）: {e}")
        return list(collected_images.values())


def search_pixabay_images(keywords: list, image_count: int = 5) -> list:
    """
    在 Pixabay 上搜索图片（采用渐进式降级搜索策略）

    Args:
        keywords: 搜索关键词列表 (按重要性从高到低排列)
        image_count: 期望获取的图片总数量，默认为 5

    Returns:
        list: 图片信息字典列表
    """
    if not PIXABAY_API_KEY:
        print("警告：未设置 PIXABAY_API_KEY 环境变量，使用占位图片")
        return []

    url = "https://pixabay.com/api/"

    current_keywords = keywords.copy()
    collected_images = {}

    # Pixabay API 查询长度限制（避免 400 错误）
    MAX_QUERY_LENGTH = 50

    try:
        while len(current_keywords) > 0 and len(collected_images) < image_count:
            # 限制查询长度，避免超过 API 限制
            current_query = " ".join(current_keywords)
            if len(current_query) > MAX_QUERY_LENGTH:
                # 如果查询过长，减少关键词数量
                current_keywords = current_keywords[:3]
                current_query = " ".join(current_keywords)

            params = {
                "key": PIXABAY_API_KEY,
                "q": current_query,
                "per_page": max(30, image_count),
                "order": "popular",
                "safesearch": "true"
            }

            response = requests.get(url, params=params, timeout=REQUESTS_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            for hit in data.get("hits", []):
                img_id = hit["id"]

                if img_id not in collected_images:
                    collected_images[img_id] = {
                        "url": hit.get("largeImageURL", ""),
                        "thumbnail": hit.get("webformatURL", ""),
                        "description": hit.get("tags", ""),
                        "photographer": hit.get("user", "Unknown")
                    }

                    if len(collected_images) >= image_count:
                        break

            if current_keywords:
                current_keywords.pop()

        return list(collected_images.values())

    except Exception as e:
        query_str = " ".join(current_keywords) if current_keywords else "Empty"
        print(f"搜索 Pixabay 时出错（当前查询组合：{query_str}）: {e}")
        return list(collected_images.values())


def download_image_with_retry(url: str, save_path: Path, max_retries: int = 3) -> bool:
    """
    下载图片到指定路径（带重试机制）

    Args:
        url: 图片 URL
        save_path: 保存路径
        max_retries: 最大重试次数

    Returns:
        bool: 是否成功
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=REQUESTS_TIMEOUT)
            response.raise_for_status()

            with open(save_path, 'wb') as f:
                f.write(response.content)

            return True

        except requests.exceptions.Timeout as e:
            last_exception = e
            if attempt < max_retries:
                delay = 2.0 * (2 ** attempt)
                print(f"  下载超时，{attempt + 1}/{max_retries}，{delay} 秒后重试...")
                time.sleep(delay)

        except requests.exceptions.ConnectionError as e:
            last_exception = e
            if attempt < max_retries:
                delay = 2.0 * (2 ** attempt)
                print(f"  下载连接错误，{attempt + 1}/{max_retries}，{delay} 秒后重试...")
                time.sleep(delay)

        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                delay = 2.0 * (2 ** attempt)
                print(f"  下载错误：{e}，{attempt + 1}/{max_retries}，{delay} 秒后重试...")
                time.sleep(delay)
            else:
                print(f"  下载失败：{e}")

    return False


def search_reference_images(concept_text: str):
    """
    搜索参考图片的主流程

    Args:
        concept_text: 设计构思文本
    """
    # 检查 API Key
    if not check_api_key():
        sys.exit(1)

    print("正在分析设计构思并提取关键词...")
    keywords = extract_keywords(concept_text)

    print(f"提取到关键词：{', '.join(keywords)}")

    # 创建保存目录
    output_dir = get_project_root() / "reference_images"
    output_dir.mkdir(exist_ok=True)

    # 搜索并下载图片
    all_images = []

    # 搜索 Unsplash 图片
    unsplash_count = 5
    unsplash_images = search_unsplash_images(keywords, unsplash_count)
    unsplash_images = unsplash_images[:5]
    all_images += unsplash_images
    print(f"共找到 {len(unsplash_images)} 张 unsplash 图片")

    # 搜索 Pixabay 图片
    pixabay_count = 5
    pixabay_images = search_pixabay_images(keywords, pixabay_count)
    pixabay_images = pixabay_images[:5]
    all_images += pixabay_images
    print(f"共找到 {len(pixabay_images)} 张 pixabay 图片")

    if not all_images:
        print("警告：未从任何平台获取到图片，将使用占位图")

    print(f"共找到 {len(all_images)} 张图片（目标：10 张），正在下载...")

    # 下载图片
    downloaded_count = 0
    for i, img_info in enumerate(all_images):
        filename = f"reference_{i + 1:02d}.jpg"
        save_path = output_dir / filename

        if download_image_with_retry(img_info["url"], save_path):
            downloaded_count += 1
            print(f"下载：{filename}")

            # 保存描述信息
            desc_path = output_dir / f"reference_{i + 1:02d}_info.txt"
            with open(desc_path, 'w', encoding='utf-8') as f:
                f.write(f"Description: {img_info.get('description', 'N/A')}\n")
                f.write(f"Photographer: {img_info.get('photographer', 'N/A')}\n")
        else:
            print(f"下载失败：{filename}")

    print(f"\n下载完成！共下载 {downloaded_count}/{len(all_images)} 张图片")
    print(f"保存目录：{output_dir}")


def main():
    # 从文件读取设计构思（如果存在）
    concept_path = get_project_root() / "design_concept.txt"
    concept_text = ""
    if concept_path.exists():
        print(f"从 {concept_path} 读取设计构思...")
        with open(concept_path, 'r', encoding='utf-8') as f:
            concept_text = f.read()
    else:
        print("或确保 design_concept.txt 文件存在于项目根目录")
        sys.exit(1)

    search_reference_images(concept_text)


if __name__ == "__main__":
    main()

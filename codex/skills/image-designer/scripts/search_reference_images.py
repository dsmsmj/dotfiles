#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
search_reference_images.py
第三步：从设计构思中提取关键词，通过 Unsplash/Pixabay 搜索参考图片

用法:
    python search_reference_images.py
"""

import os
import re
import sys
from pathlib import Path

import requests

from session_utils import get_session_root
from llm_utils import (
    generate_text_with_messages,
    translate_text,
    download_image_with_retry,
    check_api_key,
    REQUESTS_TIMEOUT,
)
from prompts import DESIGNER_SYSTEM_PROMPT

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "")


# ---------------------------------------------------------------------------
# Keyword extraction
# ---------------------------------------------------------------------------

def extract_keywords(concept_text: str) -> list:
    system_prompt = DESIGNER_SYSTEM_PROMPT + '\n你拒绝平庸的装饰，主张「设计即解决方案」。你的表达风格：精确、无废话铺垫。'
    prompt = f"""\
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

【设计构思】：
{concept_text}"""

    try:
        raw = generate_text_with_messages(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            progress_prefix="[关键词提取] ",
        )

        keywords = [kw.strip() for kw in (raw.split(',') if ',' in raw else raw.split()) if kw.strip()]
        validated = []
        for kw in keywords:
            if ' ' in kw:
                kw = kw.split()[0]
            match = re.match(r'^[a-zA-Z][a-zA-Z0-9\-]*$', kw)
            if not match:
                m = re.search(r'[a-zA-Z][a-zA-Z0-9\-]*', kw)
                kw = m.group() if m else ''
            if kw:
                validated.append(kw[:30].lower())

        en_keywords = []
        for kw in validated:
            if any('\u4e00' <= c <= '\u9fff' for c in kw):
                kw = translate_text(kw, progress_prefix="[翻译] ")
            en_keywords.append(kw)

        seen: set = set()
        unique = []
        for kw in en_keywords:
            low = kw.lower()
            if low not in seen:
                seen.add(low)
                unique.append(kw)
        return unique[:5]

    except Exception as e:
        print(f"提取关键词时出错：{e}")
        return ["modern", "design", "minimalist", "creative"]


# ---------------------------------------------------------------------------
# Unsplash / Pixabay search (progressive degradation)
# ---------------------------------------------------------------------------

def _progressive_search(keywords: list, fetch_page, image_count: int = 5) -> list:
    current = keywords.copy()
    collected: dict = {}
    while current and len(collected) < image_count:
        for item in fetch_page(" ".join(current)):
            img_id = item['id']
            if img_id not in collected:
                collected[img_id] = item
                if len(collected) >= image_count:
                    break
        if current:
            current.pop()
    return list(collected.values())


def search_unsplash_images(keywords: list, image_count: int = 5) -> list:
    if not UNSPLASH_ACCESS_KEY:
        print("警告：未设置 UNSPLASH_ACCESS_KEY")
        return []

    def fetch(query: str):
        r = requests.get(
            "https://api.unsplash.com/search/photos",
            params={"query": query, "per_page": max(30, image_count), "order_by": "relevant", "client_id": UNSPLASH_ACCESS_KEY},
            timeout=REQUESTS_TIMEOUT,
        )
        r.raise_for_status()
        return [
            {"id": x["id"], "url": x["urls"]["regular"], "description": x.get("description", ""), "photographer": x.get("user", {}).get("name", "Unknown")}
            for x in r.json().get("results", [])
        ]

    try:
        return _progressive_search(keywords, fetch, image_count)
    except Exception as e:
        print(f"搜索 Unsplash 时出错：{e}")
        return []


def search_pixabay_images(keywords: list, image_count: int = 5) -> list:
    if not PIXABAY_API_KEY:
        print("警告：未设置 PIXABAY_API_KEY")
        return []

    MAX_QUERY_LENGTH = 50

    def fetch(query: str):
        if len(query) > MAX_QUERY_LENGTH:
            query = " ".join(query.split()[:3])
        r = requests.get(
            "https://pixabay.com/api/",
            params={"key": PIXABAY_API_KEY, "q": query, "per_page": max(30, image_count), "order": "popular", "safesearch": "true"},
            timeout=REQUESTS_TIMEOUT,
        )
        r.raise_for_status()
        return [
            {"id": h["id"], "url": h.get("largeImageURL", ""), "description": h.get("tags", ""), "photographer": h.get("user", "Unknown")}
            for h in r.json().get("hits", [])
        ]

    try:
        return _progressive_search(keywords, fetch, image_count)
    except Exception as e:
        print(f"搜索 Pixabay 时出错：{e}")
        return []


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not check_api_key():
        sys.exit(1)

    session_root = get_session_root()
    concept_path = session_root / "design_concept.txt"

    if not concept_path.exists():
        print("请确保 design_concept.txt 文件存在")
        sys.exit(1)

    concept_text = concept_path.read_text(encoding='utf-8')

    print("正在分析设计构思并提取关键词...")
    keywords = extract_keywords(concept_text)
    print(f"提取到关键词：{', '.join(keywords)}")

    output_dir = session_root / "reference_images"
    output_dir.mkdir(exist_ok=True)

    all_images = search_unsplash_images(keywords, 5)[:5]
    print(f"Unsplash: {len(all_images)} 张")
    pixabay = search_pixabay_images(keywords, 5)[:5]
    print(f"Pixabay: {len(pixabay)} 张")
    all_images += pixabay

    if not all_images:
        print("警告：未从任何平台获取到图片")

    print(f"共 {len(all_images)} 张，正在下载...")

    downloaded = 0
    for i, img in enumerate(all_images):
        filename = f"reference_{i + 1:02d}.jpg"
        save_path = output_dir / filename
        try:
            download_image_with_retry(img["url"], save_path)
            downloaded += 1
            print(f"下载：{filename}")
            (output_dir / f"reference_{i + 1:02d}_info.txt").write_text(
                f"Description: {img.get('description', 'N/A')}\nPhotographer: {img.get('photographer', 'N/A')}\n",
                encoding='utf-8',
            )
        except Exception:
            print(f"下载失败：{filename}")

    print(f"\n下载完成！{downloaded}/{len(all_images)}")
    print(f"保存目录：{output_dir}")


if __name__ == "__main__":
    main()

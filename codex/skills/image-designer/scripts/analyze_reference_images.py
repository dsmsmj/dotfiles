#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze_reference_images.py
第四步：对参考图片进行设计元素分析（并发）

用法:
    python analyze_reference_images.py
"""

import sys
from pathlib import Path

from session_utils import get_session_root
from llm_utils import analyze_image_with_minimax, check_api_key
from prompts import DESIGNER_SYSTEM_PROMPT
from concurrent_utils import run_concurrent


def _analyze_one(image_path: Path) -> str:
    return analyze_image_with_minimax(
        image_path=str(image_path),
        user_prompt="请分析这张图片的风格特点和可借鉴设计元素，仅输出分析的结果，不要提供多余的说明和建议。",
        system_prompt=DESIGNER_SYSTEM_PROMPT,
    )


def main():
    if not check_api_key():
        sys.exit(1)

    session_root = get_session_root()
    ref_dir = session_root / "reference_images"

    if not ref_dir.exists():
        print("错误：reference_images 文件夹不存在，请先运行 search_reference_images.py")
        sys.exit(1)

    image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
    image_files = sorted(
        f for f in ref_dir.iterdir()
        if f.suffix.lower() in image_extensions and '_info' not in f.stem
    )

    if not image_files:
        print("错误：reference_images 文件夹中没有找到图片")
        sys.exit(1)

    print(f"找到 {len(image_files)} 张参考图片\n")

    items = [(i + 1, img) for i, img in enumerate(image_files)]
    results = run_concurrent(items, _analyze_one, label='图片分析')

    success_count = sum(1 for _, a in results if a and '分析失败' not in str(a))

    if success_count == 0:
        print(f"\n错误：所有图片分析均失败！")
        sys.exit(1)

    output_text = "# 参考图片设计元素分析报告\n\n"
    for i, (idx, analysis) in enumerate(results):
        filename = image_files[i].name
        output_text += f"## {filename}\n\n{analysis}\n\n---\n\n"

    output_path = session_root / "reference_images_analysis.txt"
    output_path.write_text(output_text, encoding='utf-8')

    print(f"\n{'=' * 60}")
    print(f"分析完成！成功：{success_count}/{len(image_files)}")
    print(f"报告已保存到：{output_path}")
    print("=" * 60)
    print(f"\n[REFERENCE_ANALYSIS_OUTPUT]\n{output_text}\n[END_REFERENCE_ANALYSIS_OUTPUT]")


if __name__ == "__main__":
    main()

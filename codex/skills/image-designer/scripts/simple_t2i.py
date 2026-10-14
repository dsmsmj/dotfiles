#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
simple_t2i.py
简化的文生图脚本 - 一键生成单张图片

用法:
    python simple_t2i.py "你的图片描述"
"""

import sys

from llm_utils import check_api_key, generate_image_with_minimax
from session_utils import get_session_subdir


def enhance_prompt(prompt: str) -> str:
    return f"""\
【角色设定】：
你是一位资深视觉设计专家，擅长生成高质量的图像描述。

【任务描述】：
请基于以下描述生成一张细节丰富、构图精美的图片：
1.严格遵循用户描述的视觉元素和风格
2.补充合理的构图、光照、色彩细节
3.仅输出生成的图片，不要提供任何文字说明

【用户描述】：
{prompt}"""


def main():
    if not check_api_key():
        sys.exit(1)

    if len(sys.argv) < 2:
        print('用法: python simple_t2i.py "你的图片描述"')
        sys.exit(1)

    user_prompt = sys.argv[1]
    print(f"正在生成图片...\n原始描述: {user_prompt}")

    enhanced = enhance_prompt(user_prompt)
    image_path = generate_image_with_minimax(
        prompt=enhanced,
        image_index=1,
        progress_prefix="[简单文生图] ",
        save_dir=get_session_subdir("output"),
    )

    if image_path and "failed" not in image_path.lower():
        print(f"\n图片生成成功: {image_path}")
        print(f"\n[GENERATED_IMAGE_1]\n{image_path}\n[END_GENERATED_IMAGE_1]")
    else:
        print(f"\n图片生成失败: {image_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()

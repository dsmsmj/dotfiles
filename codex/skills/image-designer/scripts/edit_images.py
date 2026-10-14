#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
edit_images.py
图生图编辑脚本

用法:
    python edit_images.py <图片绝对路径> "<修改要求>"
"""

import sys
import os
from pathlib import Path

from llm_utils import check_api_key, edit_image_with_minimax, download_image_with_retry, REQUESTS_TIMEOUT


def edit_image(image_path: str, edit_request: str) -> str:
    if not check_api_key():
        sys.exit(1)

    print(f"正在编辑图片：{image_path}")
    print(f"修改要求：{edit_request}\n")

    original = Path(image_path)
    original_dir = original.parent
    original_name = original.stem
    original_ext = original.suffix.lower()

    edit_number = 1
    for existing_file in original_dir.glob(f"{original_name}_edit*{original_ext}"):
        suffix = existing_file.stem.replace(f"{original_name}_edit", "")
        if suffix.startswith("_") and suffix[1:].isdigit():
            edit_number = max(edit_number, int(suffix[1:]) + 1)

    edited_path = original_dir / f"{original_name}_edit_{edit_number}{original_ext}"

    try:
        image_url = edit_image_with_minimax(
            image_path=image_path,
            edit_prompt=edit_request,
            progress_prefix="[图片编辑] ",
        )
    except Exception as e:
        print(f"\n图片编辑失败：{e}")
        return _write_error(image_path, edit_request, str(e))

    print("图片生成成功，正在下载...")

    try:
        download_image_with_retry(image_url, edited_path, timeout=REQUESTS_TIMEOUT)
        print(f"\n图片编辑完成！\n保存路径：{edited_path}")
        return str(edited_path)
    except Exception as e:
        print(f"\n图片下载失败：{e}")
        return _write_error(image_path, edit_request, f"图片下载失败：{e}")


def _write_error(image_path: str, edit_request: str, error: str) -> str:
    error_path = Path(image_path).parent / "edit_error_report.txt"
    error_path.write_text(
        f"图片编辑失败报告\n{'=' * 50}\n原图：{image_path}\n修改要求：{edit_request}\n错误：{error}\n",
        encoding='utf-8',
    )
    return str(error_path)


def main():
    if len(sys.argv) < 3:
        print('用法：python edit_images.py <图片绝对路径> "<修改要求>"')
        sys.exit(1)

    image_path = sys.argv[1]
    edit_request = sys.argv[2]

    if not os.path.exists(image_path):
        print(f"错误：图片文件不存在：{image_path}")
        sys.exit(1)

    result = edit_image(image_path, edit_request)
    print(f"\n[EDITED_IMAGE_OUTPUT]\n{result}\n[END_EDITED_IMAGE_OUTPUT]")


if __name__ == "__main__":
    main()

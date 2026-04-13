#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
edit_images.py
用户需求 B - 修改优化图片脚本

功能：
- 基于已有图片和修改要求
- 通过通义万相图生图模型 (wan2.5-i2i-preview) 直接生成优化后的图片
- 生成的图片保存到原图所在文件夹，文件名为原名称加 _edit_N 后缀（N 从 1 开始累加）

用法:
    python edit_images.py <图片绝对路径> "<修改要求>"
"""

import sys
import os
import io
from pathlib import Path

# 设置 UTF-8 编码（解决 Windows 中文乱码问题）
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
except (AttributeError, io.UnsupportedOperation, ValueError):
    pass

# 导入工具模块
from llm_utils import (
    check_api_key,
    edit_image_with_dashscope,
    download_image_with_retry,
    REQUESTS_TIMEOUT
)
import requests


def edit_image(image_path: str, edit_request: str) -> str:
    """
    编辑图片主函数

    Args:
        image_path: 原图路径（绝对路径）
        edit_request: 修改要求

    Returns:
        str: 编辑后的图片保存路径
    """
    # 检查 API Key
    if not check_api_key():
        sys.exit(1)

    print(f"正在编辑图片：{image_path}")
    print(f"修改要求：{edit_request}")
    print()

    # 获取原图所在目录
    original_dir = Path(image_path).parent
    original_name = Path(image_path).stem
    original_ext = Path(image_path).suffix.lower()

    # 生成新文件名：原名称_edit_N.扩展名（N 从 1 开始累加，避免覆盖已有编辑）
    # 查找文件夹中已有的编辑文件，确定下一个编号
    edit_number = 1
    for existing_file in original_dir.glob(f"{original_name}_edit*{original_ext}"):
        existing_name = existing_file.stem
        # 提取 _edit 后面的数字编号（如果有）
        suffix = existing_name.replace(f"{original_name}_edit", "")
        if suffix.startswith("_") and suffix[1:].isdigit():
            # 有编号的 _edit_N 文件
            num = int(suffix[1:])
            edit_number = max(edit_number, num + 1)

    edited_filename = f"{original_name}_edit_{edit_number}{original_ext}"
    edited_path = original_dir / edited_filename

    # 使用图生图模型编辑图片
    image_url = edit_image_with_dashscope(
        image_path=image_path,
        edit_prompt=edit_request,
        model="wan2.5-i2i-preview",
        progress_prefix="[图片编辑] "
    )

    if image_url is None:
        print("\n图片编辑失败")
        return create_error_report(image_path, edit_request, "图生图 API 调用失败")

    print(f"图片生成成功，正在下载...")

    # 下载图片
    if download_image_with_retry(image_url, edited_path, timeout=REQUESTS_TIMEOUT):
        print(f"\n图片编辑完成！")
        print(f"保存路径：{edited_path}")
        return str(edited_path)
    else:
        print(f"\n图片下载失败")
        return create_error_report(image_path, edit_request, "图片下载失败")


def create_error_report(image_path: str, edit_request: str, error: str) -> str:
    """
    创建错误报告文件

    Args:
        image_path: 原图路径
        edit_request: 修改要求
        error: 错误信息

    Returns:
        str: 错误报告路径
    """
    # 错误报告保存到原图所在目录
    output_dir = Path(image_path).parent
    output_dir.mkdir(exist_ok=True)

    error_path = output_dir / f"edit_error_report.txt"
    with open(error_path, 'w', encoding='utf-8') as f:
        f.write("图片编辑失败报告\n")
        f.write("=" * 50 + "\n")
        f.write(f"原图：{image_path}\n")
        f.write(f"修改要求：{edit_request}\n")
        f.write(f"错误：{error}\n")

    return str(error_path)


def main():
    if len(sys.argv) < 3:
        print("用法：python edit_images.py <图片绝对路径> \"<修改要求>\"")
        print("\n示例:")
        print('  python edit_images.py "C:/Users/Pictures/design.png" "让图片更明亮一些"')
        print('  python edit_images.py "D:/Work/banner.jpg" "增加现代感，使用蓝色调"')
        sys.exit(1)

    image_path = sys.argv[1]
    edit_request = sys.argv[2]

    if not os.path.exists(image_path):
        print(f"错误：图片文件不存在：{image_path}")
        sys.exit(1)

    edited_path = edit_image(image_path, edit_request)

    if "failed" in edited_path or "error" in edited_path.lower():
        print(f"\n图片编辑失败，错误记录已保存到：{edited_path}")
    else:
        print(f"\n图片编辑完成！")
        print(f"保存路径：{edited_path}")

    # 输出结果
    print(f"\n[EDITED_IMAGE_OUTPUT]\n{edited_path}\n[END_EDITED_IMAGE_OUTPUT]")


if __name__ == "__main__":
    main()

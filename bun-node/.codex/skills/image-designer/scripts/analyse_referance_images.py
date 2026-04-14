#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyse_referance_images.py
第四步：分析参考图片脚本

功能：
- 对 reference_images 文件夹中的图片通过 Qwen 视觉模型进行设计元素分析
- 使用异步并发方式提高效率
- 生成纯文本形式的设计元素分析文本

用法:
    python analyse_referance_images.py
"""

import sys
import os
import io
import asyncio
from pathlib import Path
from typing import List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor

# 设置 UTF-8 编码（解决 Windows 中文乱码问题）
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
except (AttributeError, io.UnsupportedOperation, ValueError):
    pass

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent

# 导入工具模块
from session_utils import get_session_root, get_session_subdir
from llm_utils import (
    analyze_image_with_qwen_vl,
    check_api_key,
    MAX_CONCURRENT_TASKS
)

# 全局进度变量
_completed_count = 0
_total_count = 0
_progress_lock = asyncio.Lock()


def get_project_root() -> Path:
    """获取当前 session 的工作根目录（而非项目根目录）"""
    return get_session_root()


def analyze_image_with_qwen(image_path: str) -> str:
    """
    使用 Qwen 视觉模型分析图片的设计元素

    Args:
        image_path: 图片路径

    Returns:
        str: 设计元素分析结果
    """
    system_prompt = """
【角色设定】：
你是一位资深视觉设计专家，擅长内容如下：
1. 品牌与标识设计，包括：Logo 设计，品牌视觉识别系统，名片、信纸等品牌物料。
2. 营销与广告设计，包括：社交媒体海报与横幅，电商产品主图、详情图，促销广告、活动海报，宣传单页、传单。
3. 创意与艺术设计，包括：插画与概念艺术，IP 形象与吉祥物设计，艺术风格化图像，封面设计（书籍、专辑等）。
4. 图像编辑与处理，包括：图片修改与优化，风格转换（如照片转插画），多图合成，背景替换。
5. 内容创作，包括：社交媒体配图，文章/博客封面图，演示文稿视觉素材，节日贺卡。
"""
    user_prompt = "请分析这张图片的风格特点和可借鉴设计元素，仅输出分析的结果，不要提供多余的说明和建议。"

    return analyze_image_with_qwen_vl(
        image_path=image_path,
        user_prompt=user_prompt,
        system_prompt=system_prompt,
        progress_prefix=""
    )


async def analyze_image_async(image_path: Path, semaphore: asyncio.Semaphore,
                               executor: ThreadPoolExecutor) -> Tuple[str, str]:
    """
    异步分析单张图片

    Args:
        image_path: 图片路径
        semaphore: 信号量，控制并发数
        executor: 线程池执行器

    Returns:
        Tuple[str, str]: (文件名，分析结果)
    """
    global _completed_count, _total_count

    async with semaphore:
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                executor,
                lambda: analyze_image_with_qwen(str(image_path))
            )

            async with _progress_lock:
                _completed_count += 1
                if "分析失败" not in result:
                    print(f"  ✓ [{_completed_count}/{_total_count}] {image_path.name}: 分析完成")
                else:
                    print(f"  ✗ [{_completed_count}/{_total_count}] {image_path.name}: 分析失败")

            return image_path.name, result
        except Exception as e:
            async with _progress_lock:
                _completed_count += 1
                print(f"  ✗ [{_completed_count}/{_total_count}] {image_path.name}: 异常 - {str(e)}")
            return image_path.name, f"[分析失败：{str(e)}]"


async def analyze_all_images_async(image_files: List[Path]) -> List[Dict]:
    """
    异步并发分析所有图片

    Args:
        image_files: 图片文件列表

    Returns:
        List[Dict]: 分析结果列表
    """
    global _completed_count, _total_count
    _completed_count = 0
    _total_count = len(image_files)

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

    # 创建共享线程池，所有任务共用
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_TASKS) as executor:
        tasks = [analyze_image_async(img_path, semaphore, executor) for img_path in image_files]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    all_analyses = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            all_analyses.append({
                "filename": image_files[i].name,
                "analysis": f"[分析失败：{str(result)}]"
            })
        else:
            filename, analysis = result
            all_analyses.append({
                "filename": filename,
                "analysis": analysis
            })

    return all_analyses


def analyze_all_reference_images():
    """
    分析所有参考图片的主流程（异步并发版本）
    """
    # 检查 API Key
    if not check_api_key():
        sys.exit(1)

    # 获取参考图片目录
    ref_dir = get_project_root() / "reference_images"

    if not ref_dir.exists():
        print("错误：reference_images 文件夹不存在")
        print("请先运行第三步：search_referance_images.py")
        sys.exit(1)

    # 获取所有图片文件
    image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
    image_files = [
        f for f in ref_dir.iterdir()
        if f.suffix.lower() in image_extensions and '_info' not in f.stem
    ]

    if not image_files:
        print("错误：reference_images 文件夹中没有找到图片")
        sys.exit(1)

    num_images = len(image_files)
    print(f"找到 {num_images} 张参考图片，开始异步并发分析...")
    print(f"最大并发数：{MAX_CONCURRENT_TASKS}")
    estimated_time = num_images / MAX_CONCURRENT_TASKS * 1.5
    print(f"预计时间：约 {estimated_time:.1f} 分钟（并行处理，串行时间约 {num_images * 1.5} 分钟）\n")
    print("分析进度：")

    # 运行异步分析
    all_analyses = asyncio.run(analyze_all_images_async(sorted(image_files)))

    # 统计成功数量
    success_count = sum(1 for item in all_analyses if "分析失败" not in item["analysis"])

    # 检查是否全部失败
    if success_count == 0:
        print(f"\n{'='*60}")
        print("错误：所有图片分析均失败！")
        print(f"成功：{success_count}/{num_images}")
        print("="*60)
        print("\n请检查 API 状态或参考图片文件")
        sys.exit(1)

    # 生成综合分析报告
    output_text = "# 参考图片设计元素分析报告\n\n"

    for item in all_analyses:
        output_text += f"## {item['filename']}\n\n"
        output_text += f"{item['analysis']}\n\n"
        output_text += "---\n\n"

    # 保存分析结果
    output_path = get_project_root() / "reference_images_analysis.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_text)

    print(f"\n{'='*60}")
    print("分析完成！")
    print(f"成功：{success_count}/{num_images}")
    print(f"分析报告已保存到：{output_path}")
    print("="*60)

    # 输出分析内容供下一步使用
    print(f"\n[REFERENCE_ANALYSIS_OUTPUT]\n{output_text}\n[END_REFERENCE_ANALYSIS_OUTPUT]")


def main():
    analyze_all_reference_images()


if __name__ == "__main__":
    main()

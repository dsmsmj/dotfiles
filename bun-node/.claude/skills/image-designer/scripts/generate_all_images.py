#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_all_images.py
第七步增强版：一次性生成所有 4 张图片

功能：
- 读取 design_plans/ 文件夹中的 4 份设计计划
- 通过 Qwen 文生图模型生成 4 张图片
- 保存到 output/ 文件夹

用法:
    python generate_all_images.py
"""

import sys
import os
import io
import asyncio
from pathlib import Path
from typing import List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor

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
    generate_image_with_dashscope,
    check_api_key,
    MAX_CONCURRENT_TASKS
)

# 全局进度变量
_completed_count = 0
_total_count = 0
_progress_lock = asyncio.Lock()


def get_project_root() -> Path:
    """获取当前 session 的工作根目录"""
    return get_session_root()


def build_image_prompt(design_plan: str) -> str:
    """
    构建图片生成 prompt

    Args:
        design_plan: 设计计划文本

    Returns:
        str: 增强后的 prompt
    """
    return f"""
【角色设定】：
你是一位资深视觉设计专家，擅长内容如下：
1.品牌与标识设计，包括：Logo 设计，品牌视觉识别系统，名片、信纸等品牌物料。
2.营销与广告设计，包括：社交媒体海报与横幅，电商产品主图、详情图，促销广告、活动海报，宣传单页、传单。
3.创意与艺术设计，包括：插画与概念艺术，IP 形象与吉祥物设计，艺术风格化图像，封面设计（书籍、专辑等）。
4.图像编辑与处理，包括：图片修改与优化，风格转换（如照片转插画），多图合成，背景替换。
5.内容创作，包括：社交媒体配图，文章/博客封面图，演示文稿视觉素材，节日贺卡。

【任务描述】：
请基于以下标准生成一张图片：
1.严格参考【设计计划】，同时根据最佳美学构图进行图片创作。
2.生成的图片必须为全新设计，禁止使用任何互联网图片。
3.生成的图片中严禁使用任何【设计计划】未提供的文字内容。
4.仅输出生成的图片，不要提供任何文字说明。

【设计计划】：
{design_plan}
"""


async def generate_image_async(design_plan: str, image_index: int, output_dir: Path,
                                semaphore: asyncio.Semaphore,
                                executor: ThreadPoolExecutor) -> Tuple[int, str]:
    """
    异步生成单张图片

    Args:
        design_plan: 设计计划文本
        image_index: 图片编号（1-4）
        output_dir: 输出目录
        semaphore: 信号量，控制并发数
        executor: 线程池执行器

    Returns:
        Tuple[int, str]: (图片编号，图片路径)
    """
    global _completed_count, _total_count

    async with semaphore:
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                executor,
                lambda: _generate_image_sync(design_plan, image_index, output_dir)
            )

            async with _progress_lock:
                _completed_count += 1
                if result and "failed" not in result.lower():
                    print(f"  ✓ [{_completed_count}/{_total_count}] 图片 {image_index}: 生成成功")
                else:
                    print(f"  ✗ [{_completed_count}/{_total_count}] 图片 {image_index}: 生成失败")

            return image_index, result
        except Exception as e:
            async with _progress_lock:
                _completed_count += 1
                print(f"  ✗ [{_completed_count}/{_total_count}] 图片 {image_index}: 异常 - {str(e)}")
            return image_index, f"[生成失败：{str(e)}]"


def _generate_image_sync(design_plan: str, image_index: int, output_dir: Path) -> str:
    """同步生成图片（在线程池中执行）"""
    enhanced_prompt = build_image_prompt(design_plan)

    image_path = generate_image_with_dashscope(
        prompt=enhanced_prompt,
        image_index=image_index,
        progress_prefix="",
        save_dir=output_dir
    )
    return image_path


async def generate_all_images_async(plan_contents: List[Tuple[int, str]],
                                     output_dir: Path) -> List[Optional[str]]:
    """
    异步并发生成所有图片

    Args:
        plan_contents: [(图片编号，设计计划文本), ...]
        output_dir: 输出目录

    Returns:
        List[Optional[str]]: [图片路径 1, 图片路径 2, ...]（按输入顺序对齐，失败则为 None）
    """
    global _completed_count, _total_count
    _completed_count = 0
    _total_count = len(plan_contents)

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_TASKS) as executor:
        tasks = [
            generate_image_async(plan_text, img_idx, output_dir, semaphore, executor)
            for img_idx, plan_text in plan_contents
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # 按输入顺序返回结果（与 plan_contents 一一对应）
    image_paths = [None] * len(plan_contents)
    for result in results:
        if isinstance(result, Exception):
            print(f"图片生成异常：{str(result)}")
        elif isinstance(result, tuple) and len(result) == 2:
            idx, path = result
            # 找到输入中对应的索引位置
            for i, (input_idx, _) in enumerate(plan_contents):
                if input_idx == idx:
                    image_paths[i] = path
                    break

    return image_paths


def main():
    # 检查 API Key
    if not check_api_key():
        sys.exit(1)

    # 获取设计计划目录
    plans_dir = get_project_root() / "design_plans"

    if not plans_dir.exists():
        print("错误：design_plans 文件夹不存在")
        print("请先运行第六步：generate_all_design_plans.py")
        sys.exit(1)

    # 获取所有设计计划文件
    plan_files = sorted(plans_dir.glob("design_plan_*.txt"))

    # 排除可能存在的合并文件
    plan_files = [f for f in plan_files if f.name != "design_plans_merged.txt"]

    if len(plan_files) < 4:
        print(f"警告：design_plans 文件夹中只有 {len(plan_files)} 份设计计划（期望 4 份）")
        print("请确保已运行第六步生成所有设计计划")

    # 创建输出目录
    output_dir = get_project_root() / "output"
    output_dir.mkdir(exist_ok=True)

    num_images = min(len(plan_files), 4)
    print(f"准备生成 {num_images} 张图片...")
    print(f"最大并发数：{MAX_CONCURRENT_TASKS}")
    estimated_time = num_images / MAX_CONCURRENT_TASKS * 2.5
    print(f"预计时间：约 {estimated_time:.1f} 分钟（并行处理，串行时间约 {num_images * 2.5} 分钟）\n")

    # 读取设计计划内容
    plan_contents = []
    for i in range(1, 5):
        plan_file = plans_dir / f"design_plan_{i}.txt"
        if plan_file.exists():
            with open(plan_file, 'r', encoding='utf-8') as f:
                plan_contents.append((i, f.read()))
        else:
            print(f"警告：设计计划 {i} 不存在，跳过")

    if not plan_contents:
        print("错误：没有找到任何设计计划")
        sys.exit(1)

    # 检查已存在的图片
    existing_images = []
    to_generate = []
    for img_idx, plan_text in plan_contents:
        existing_image = output_dir / f"generated_image_{img_idx}.png"
        if existing_image.exists():
            print(f"图片 {img_idx} 已存在，跳过")
            existing_images.append((img_idx, str(existing_image)))
        else:
            to_generate.append((img_idx, plan_text))

    generated_images = [None] * len(plan_contents)

    # 记录已存在的图片
    for img_idx, img_path in existing_images:
        generated_images[img_idx - 1] = img_path

    # 异步并发生成剩余图片
    if to_generate:
        print(f"\n开始异步并发生成图片...")
        print("分析进度：")

        # 运行异步生成
        raw_results = asyncio.run(generate_all_images_async(to_generate, output_dir))

        # 按索引保存结果（raw_results 与 to_generate 一一对应）
        for i, img_path in enumerate(raw_results):
            if img_path and "failed" not in img_path.lower():
                img_idx = to_generate[i][0]  # 获取原始图片编号
                generated_images[img_idx - 1] = img_path

    # 统计成功数量
    success_count = sum(1 for p in generated_images if p and "failed" not in p.lower())

    print(f"\n{'='*60}")
    if success_count == 0:
        print("所有图片生成失败！")
        print(f"成功：{success_count}/{len(generated_images)}")
        print("="*60)
        print("\n错误：没有成功生成任何图片，请检查 API 状态或设计计划")
        sys.exit(1)
    else:
        print("所有图片生成完成！")
        print(f"成功：{success_count}/{len(generated_images)}")
        print("="*60)

    # 输出结果
    for i, img_path in enumerate(generated_images, 1):
        if img_path and "failed" not in img_path.lower():
            print(f"\n[GENERATED_IMAGE_{i}]\n{img_path}\n[END_GENERATED_IMAGE_{i}]")


if __name__ == "__main__":
    main()

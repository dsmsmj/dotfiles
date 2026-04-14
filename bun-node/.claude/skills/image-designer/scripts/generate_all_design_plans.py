#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_all_design_plans.py
第六步增强版：一次性生成所有 4 种风格的设计计划

功能：
- 读取 design_strategy.txt 中的 4 种风格
- 为每种风格生成详细的设计计划
- 保存到 design_plans/ 文件夹

用法:
    python generate_all_design_plans.py
"""

import sys
import os
import io
import re
import asyncio
from pathlib import Path
from typing import List, Optional
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
    generate_text_with_messages,
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


DESIGN_PLAN_SYSTEM_PROMPT = """
【角色设定】：
你是一位资深视觉设计专家，擅长内容如下：
1. 品牌与标识设计，包括：Logo 设计，品牌视觉识别系统，名片、信纸等品牌物料。
2. 营销与广告设计，包括：社交媒体海报与横幅，电商产品主图、详情图，促销广告、活动海报，宣传单页、传单。
3. 创意与艺术设计，包括：插画与概念艺术，IP 形象与吉祥物设计，艺术风格化图像，封面设计（书籍、专辑等）。
4. 图像编辑与处理，包括：图片修改与优化，风格转换（如照片转插画），多图合成，背景替换。
5. 内容创作，包括：社交媒体配图，文章/博客封面图，演示文稿视觉素材，节日贺卡。
"""


def parse_strategy_styles(strategy_text: str) -> List[str]:
    """
    从设计策略文本中解析出 4 种风格描述（使用 Qwen 模型智能提取）

    Args:
        strategy_text: 设计策略文本

    Returns:
        List[str]: 包含 4 个风格描述的列表
    """
    system_prompt = """你是一位专业的设计文档分析师。你的任务是从设计策略文本中提取 4 种不同设计风格的完整名称。

请遵循以下规则：
1. 识别文本中的 4 种设计风格（通常标注为"方案一/二/三/四"、"风格 1/2/3/4"、"Style 1/2/3/4"等）
2. 提取每种风格的完整名称
3. 按顺序返回 4 种风格的名称，每种风格之间用"|||"分隔

输出格式示例：
风格 1 完整名称|||风格 2 完整名称|||风格 3 完整名称|||风格 4 完整名称"""

    user_prompt = f"""请从以下设计策略文本中提取 4 种风格的完整名称

{strategy_text}

请按顺序提取 4 种风格，用"|||"分隔每种风格的描述。"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    extracted_text = generate_text_with_messages(
        messages=messages,
        model="qwen-max-latest",
        temperature=0.3,
        progress_prefix="[风格解析] "
    )

    # 使用"|||"分隔符分割 4 种风格
    styles = [s.strip() for s in extracted_text.split("|||") if s.strip()]

    # 如果提取的风格不足 4 个，使用正则表达式备用解析
    if len(styles) < 4:
        print(f"  提示：Qwen 提取到 {len(styles)} 种风格，使用正则表达式解析...")
        return fallback_parse_styles(strategy_text)

    return styles[:4]  # 确保只返回 4 个


def fallback_parse_styles(strategy_text: str) -> List[str]:
    """
    备用解析方案：使用正则表达式解析风格

    Args:
        strategy_text: 设计策略文本

    Returns:
        List[str]: 包含 4 个风格描述的列表
    """
    styles = []

    # 尝试匹配 "#### 1. 风格名" 或 "### 1. 风格名" 格式
    pattern = r'(?:####|###)\s*\d+\.?\s*([^\n]+)\n(?:.*?(?=(?:####|###)\s*\d+))?'
    matches = re.findall(pattern, strategy_text, re.DOTALL)

    if len(matches) >= 4:
        styles = [m.strip() for m in matches[:4]]
    else:
        # 尝试按章节分割
        sections = re.split(r'(?:###|####)', strategy_text)
        for section in sections:
            section = section.strip()
            if len(section) > 50:
                styles.append(section)

    # 确保正好有 4 个风格
    if len(styles) < 4:
        styles = [strategy_text] * 4

    return styles[:4]


def build_design_plan_messages(strategy_text: str, style_name: str) -> list:
    """构建设计计划的 messages"""
    prompt = f"""
【任务描述】：
请基于以下标准提供一份精练的英文设计计划（可直接用于 AI 文生图）：
1. 设计计划须基于【设计策略】中由【采用设计风格】指出的设计风格信息进行完整的图片设计说明。
2. 设计计划须简洁明了，避免重复描述相同的内容。
3. 图片中只允许使用【采用设计风格】在【设计策略】中对应设计风格指定使用的文字和数据，严禁使用较长的文字描述。
4. 如需引用【采用设计风格】在【设计策略】中对应设计风格提及的名称类文本，必须使用其原名称。
5. 设计计划中必须根据【采用设计风格】在【设计策略】中对应设计风格的要求，说明图片所采用的语言以及尺寸。
6. 风格灵魂优先，【采用设计风格】在【设计策略】对应设计风格所描述的设计理念、视觉秩序与空间感是最高准则。
7. 拒绝死板执行，严禁机械套用【设计策略】内容，信息层级、文字排版等须根据最佳美学实践进行设计。
8. 仅以文字方式直接输出设计计划的内容，严禁在提供设计计划之后进行任何形式的询问和说明。

【设计策略】：
{strategy_text}

【采用设计风格】：
{style_name}
"""
    return [
        {"role": "system", "content": DESIGN_PLAN_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]


async def generate_design_plan_async(style_name: str, style_index: int,
                                      semaphore: asyncio.Semaphore,
                                      executor: ThreadPoolExecutor,
                                      strategy_text: str) -> tuple:
    """
    异步生成单个设计计划

    Args:
        style_name: 风格名称
        style_index: 风格编号（1-4）
        semaphore: 信号量，控制并发数
        executor: 线程池执行器
        strategy_text: 完整的设计策略文本

    Returns:
        tuple: (风格编号，设计计划文本或 None)
    """
    global _completed_count, _total_count

    async with semaphore:
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                executor,
                lambda: _generate_design_plan_sync(strategy_text, style_name, style_index)
            )

            async with _progress_lock:
                _completed_count += 1
                if result:
                    print(f"  ✓ [{_completed_count}/{_total_count}] 设计计划 {style_index}: 生成完成")
                else:
                    print(f"  ✗ [{_completed_count}/{_total_count}] 设计计划 {style_index}: 生成失败")

            return style_index, result
        except Exception as e:
            async with _progress_lock:
                _completed_count += 1
                print(f"  ✗ [{_completed_count}/{_total_count}] 设计计划 {style_index}: 异常 - {str(e)}")
            return style_index, None


def _generate_design_plan_sync(strategy_text: str, style_name: str, style_index: int) -> Optional[str]:
    """同步生成设计计划（在线程池中执行）"""
    messages = build_design_plan_messages(strategy_text, style_name)

    try:
        design_plan = generate_text_with_messages(
            messages=messages,
            model="qwen-max-latest",
            temperature=0.7,
            progress_prefix=""
        )
        return design_plan if design_plan else None
    except Exception as e:
        print(f"生成设计计划 {style_index} 时出错：{e}")
        return None


async def generate_all_design_plans_async(strategy_text: str, styles: List[str]) -> List[Optional[str]]:
    """
    异步并发生成所有设计计划

    Args:
        strategy_text: 设计策略文本
        styles: 风格列表

    Returns:
        List[Optional[str]]: [设计计划 1, 设计计划 2, ...]（按索引对齐，失败则为 None）
    """
    global _completed_count, _total_count
    _completed_count = 0
    _total_count = len(styles)

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_TASKS) as executor:
        tasks = [
            generate_design_plan_async(style, i + 1, semaphore, executor, strategy_text)
            for i, style in enumerate(styles)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # 按原始顺序返回结果（只返回设计计划文本，按索引对齐）
    plans = [None] * len(styles)
    for result in results:
        if isinstance(result, Exception):
            print(f"设计计划生成异常：{str(result)}")
        elif isinstance(result, tuple) and len(result) == 2:
            idx, plan = result
            plans[idx - 1] = plan

    return plans


def main():
    # 检查 API Key
    if not check_api_key():
        sys.exit(1)

    # 读取设计策略文件
    strategy_path = get_project_root() / "design_strategy.txt"

    if not strategy_path.exists():
        print("错误：design_strategy.txt 文件不存在")
        print("请先运行第五步：generate_design_strategy.py")
        sys.exit(1)

    with open(strategy_path, 'r', encoding='utf-8') as f:
        strategy_text = f.read()

    # 解析出 4 种风格（使用 Qwen 模型）
    print("正在使用 Qwen 模型解析设计策略中的 4 种风格...\n")
    styles = parse_strategy_styles(strategy_text)

    print(f"从设计策略中解析出 {len(styles)} 种风格")

    # 创建输出目录
    output_dir = get_project_root() / "design_plans"
    output_dir.mkdir(exist_ok=True)

    # 异步并发生成所有设计计划
    print(f"\n开始异步并发生成设计计划...")
    print(f"最大并发数：{MAX_CONCURRENT_TASKS}")
    estimated_time = len(styles) / MAX_CONCURRENT_TASKS * 45
    print(f"预计时间：约 {estimated_time:.1f} 秒（并行处理，串行时间约 {len(styles) * 45} 秒）\n")
    print("分析进度：")

    # 运行异步分析
    raw_results = asyncio.run(generate_all_design_plans_async(strategy_text, styles))

    # 保存结果
    design_plans = []
    for i, plan in enumerate(raw_results):
        style_idx = i + 1  # 风格编号从 1 开始

        if plan:
            design_plans.append((style_idx, plan))

            # 保存到文件
            output_path = output_dir / f"design_plan_{style_idx}.txt"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(plan)
        else:
            design_plans.append((style_idx, None))

    # 输出统计
    success_count = sum(1 for _, p in design_plans if p)

    print(f"\n{'='*60}")
    if success_count == 0:
        print("错误：所有设计计划均生成失败！")
        print(f"成功：{success_count}/4")
        print("="*60)
        print("\n请检查 API 状态或 design_strategy.txt 内容")
        sys.exit(1)
    else:
        print("所有设计计划生成完成！")
        print(f"成功：{success_count}/4")
        print("="*60)

    # 输出结果供下一步使用
    for i, plan in design_plans:
        if plan:
            print(f"\n[DESIGN_PLAN_{i}_OUTPUT]\n{plan}\n[END_DESIGN_PLAN_{i}_OUTPUT]")


if __name__ == "__main__":
    main()

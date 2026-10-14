#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_all_design_plans.py
第六步：一次性生成所有 4 种风格的设计计划

用法:
    python generate_all_design_plans.py
"""

import re
import sys
from typing import List, Optional

from session_utils import get_session_root
from llm_utils import generate_text_with_messages, check_api_key
from prompts import DESIGNER_SYSTEM_PROMPT
from concurrent_utils import run_concurrent


def parse_strategy_styles(strategy_text: str) -> List[str]:
    """从设计策略文本中解析出 4 种风格描述（先用 LLM 提取，失败则正则兜底）"""
    system_prompt = """\
你是一位专业的设计文档分析师。你的任务是从设计策略文本中提取 4 种不同设计风格的完整名称。

请遵循以下规则：
1. 识别文本中的 4 种设计风格（通常标注为"方案一/二/三/四"、"风格 1/2/3/4"、"Style 1/2/3/4"等）
2. 提取每种风格的完整名称
3. 按顺序返回 4 种风格的名称，每种风格之间用"|||"分隔

输出格式示例：
风格 1 完整名称|||风格 2 完整名称|||风格 3 完整名称|||风格 4 完整名称"""

    user_prompt = f"请从以下设计策略文本中提取 4 种风格的完整名称\n\n{strategy_text}\n\n请按顺序提取 4 种风格，用 ||| 分隔每种风格的描述。"

    extracted = generate_text_with_messages(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        progress_prefix="[风格解析] ",
    )

    styles = [s.strip() for s in extracted.split("|||") if s.strip()]
    if len(styles) >= 4:
        return styles[:4]

    print(f"  提示：模型提取到 {len(styles)} 种风格，使用正则表达式解析...")
    return _fallback_parse(strategy_text)


def _fallback_parse(strategy_text: str) -> List[str]:
    pattern = r'(?:####|###)\s*\d+\.?\s*([^\n]+)\n(?:.*?(?=(?:####|###)\s*\d+))?'
    matches = re.findall(pattern, strategy_text, re.DOTALL)
    if len(matches) >= 4:
        return [m.strip() for m in matches[:4]]

    sections = re.split(r'(?:###|####)', strategy_text)
    styles = [s.strip() for s in sections if len(s.strip()) > 50]
    if len(styles) >= 4:
        return styles[:4]

    return [strategy_text] * 4


def _build_plan_messages(strategy_text: str, style_name: str) -> list:
    prompt = f"""\
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
{style_name}"""
    return [
        {"role": "system", "content": DESIGNER_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]


def _generate_one_plan(payload: dict) -> Optional[str]:
    messages = _build_plan_messages(payload['strategy'], payload['style'])
    return generate_text_with_messages(messages=messages, temperature=0.7)


def main():
    if not check_api_key():
        sys.exit(1)

    session_root = get_session_root()
    strategy_path = session_root / "design_strategy.txt"

    if not strategy_path.exists():
        print("错误：design_strategy.txt 文件不存在，请先运行 generate_design_strategy.py")
        sys.exit(1)

    strategy_text = strategy_path.read_text(encoding='utf-8')

    print("正在解析设计策略中的 4 种风格...\n")
    styles = parse_strategy_styles(strategy_text)
    print(f"解析出 {len(styles)} 种风格\n")

    output_dir = session_root / "design_plans"
    output_dir.mkdir(exist_ok=True)

    items = [
        (i + 1, {'strategy': strategy_text, 'style': style})
        for i, style in enumerate(styles)
    ]

    results = run_concurrent(items, _generate_one_plan, label='设计计划')

    success_count = 0
    for idx, plan in results:
        if plan:
            success_count += 1
            (output_dir / f"design_plan_{idx}.txt").write_text(plan, encoding='utf-8')

    print(f"\n{'=' * 60}")
    print(f"设计计划生成完成！成功：{success_count}/4")
    print("=" * 60)

    if success_count == 0:
        print("\n请检查 API 状态或 design_strategy.txt 内容")
        sys.exit(1)

    for idx, plan in results:
        if plan:
            print(f"\n[DESIGN_PLAN_{idx}_OUTPUT]\n{plan}\n[END_DESIGN_PLAN_{idx}_OUTPUT]")


if __name__ == "__main__":
    main()

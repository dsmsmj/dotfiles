#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_design_strategy.py
第五步：基于设计构思和参考图分析，生成包含 4 种风格的设计策略

用法:
    python generate_design_strategy.py
"""

import sys

from session_utils import get_session_root
from llm_utils import generate_text_with_messages, check_api_key
from prompts import DESIGNER_SYSTEM_PROMPT


def build_messages(concept: str, analysis: str, doc_content: str = '') -> list:
    prompt = f"""\
【任务描述】：
基于以下标准并考虑视觉美学提供一份设计策略：
1.设计策略须参照【参考图片分析】中不同图片的特点和可借鉴元素，总结出4种完全不同类型的设计风格（设计风格须各具特色，避免相似的视觉呈现效果）。
2.每种设计风格须提供设计风格名称——XXXX风，并用一句话描述该设计风格通过什么方式实现什么目的。
3.每种设计风格都须结合【设计构思】和【材料文本】，精准地描述基于该风格的具体图片设计要求，确保能通过描述的内容指导AI生成图片。
4.每种设计风格都必须具体描述详图片的各项设计要点，包括其具体的内容信息及排版。
5.每种设计风格须基于【设计构思】，分别指明图片内容所须采用的语言以及图片尺寸。
6.每种设计风格中，须根据最佳页面设计明确说明如何展示必要的文字和数据（文字和数据的实际内容必须提供），展示的文字必须简洁（严禁使用较长的文字描述），数据尽可能设计为简洁的图表展示。
7.严禁提及任何参考图片/表格的名称。
8.仅以文字方式输出设计策略的内容，严禁在提供设计策略之后进行任何形式的询问。

【设计构思】：
{concept}

【材料文本】：
{doc_content}

【参考图片分析】：
{analysis}"""
    return [
        {"role": "system", "content": DESIGNER_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]


def generate_design_strategy(concept: str, analysis: str, doc_content: str = '') -> str:
    messages = build_messages(concept, analysis, doc_content)
    try:
        return generate_text_with_messages(
            messages=messages,
            temperature=0.8,
            progress_prefix="[设计策略] ",
        )
    except Exception as e:
        print(f"生成设计策略时出错：{e}")
        sys.exit(1)


def main():
    if not check_api_key():
        sys.exit(1)

    session_dir = get_session_root()

    concept_path = session_dir / "design_concept.txt"
    analysis_path = session_dir / "reference_images_analysis.txt"
    extracted_path = session_dir / "extracted_text.txt"

    if not concept_path.exists() or not analysis_path.exists():
        print("请确保 design_concept.txt 和 reference_images_analysis.txt 存在")
        sys.exit(1)

    concept = concept_path.read_text(encoding='utf-8')
    analysis = analysis_path.read_text(encoding='utf-8')
    doc_content = extracted_path.read_text(encoding='utf-8') if extracted_path.exists() else ''

    print("正在生成设计策略（可能需要 30-60 秒）...")
    strategy = generate_design_strategy(concept, analysis, doc_content)

    print("\n" + "=" * 60)
    print("设计策略（4 种风格方案）")
    print("=" * 60)
    print(strategy)
    print("=" * 60 + "\n")

    output_path = session_dir / "design_strategy.txt"
    output_path.write_text(strategy, encoding='utf-8')
    print(f"设计策略已保存到：{output_path}")
    print(f"\n[DESIGN_STRATEGY_OUTPUT]\n{strategy}\n[END_DESIGN_STRATEGY_OUTPUT]")


if __name__ == "__main__":
    main()

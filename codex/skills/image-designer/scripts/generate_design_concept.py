#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_design_concept.py
第二步：生成设计构思

用法:
    python generate_design_concept.py "<合并后的 prompt>"
"""

import sys
from pathlib import Path

from session_utils import get_session_root
from llm_utils import generate_text_with_messages, check_api_key
from prompts import DESIGNER_SYSTEM_PROMPT


def build_messages(user_input: str, doc_content: str) -> list:
    prompt = f"""\
【任务描述】：
请基于【任务要求】以及【材料文本】的内容，遵循以下规则生成一段符合视觉美学的设计构思：
1.如果【材料文本】内容为空，则仅遵循【任务要求】。
2.设计构思中必须根据【任务要求】指明当前任务的具体要求。
3.设计构思中必须指明图片内容所采用的语言，语言优先根据【任务要求】确定，若【任务要求】中未指明所需的语言，则使用与【任务要求】内文本相同的语言。
4.设计构思中必须指明所采用的图片尺寸，必须使用满足【任务要求】的最佳尺寸。
5.设计构思中禁止说明图片的具体内容（包括文字、数据、排版、布局等）。
6.设计构思须内容简洁，采用分段式结构，严禁在提供设计构思之后进行任何形式的询问。
7.生成设计构思时可参考以下设计原则（但不要死板套用）：
\t-色彩心理学
\t-设计趋势
\t-需求分析

【任务要求】：
{user_input}

【材料文本】：
{doc_content}"""
    return [
        {"role": "system", "content": DESIGNER_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]


def generate_design_concept(user_input: str, doc_content: str) -> str:
    messages = build_messages(user_input, doc_content)
    try:
        return generate_text_with_messages(
            messages=messages,
            temperature=0.7,
            progress_prefix="[设计构思] ",
        )
    except Exception as e:
        print(f"生成设计构思时出错：{e}")
        sys.exit(1)


def main():
    if not check_api_key():
        sys.exit(1)

    user_input = sys.argv[1] if len(sys.argv) >= 2 else ""

    session_root = get_session_root()
    extracted_path = session_root / "extracted_text.txt"
    doc_content = ""
    if extracted_path.exists():
        print(f"\n从 {extracted_path} 读取文档内容...")
        doc_content = extracted_path.read_text(encoding='utf-8')

    print("正在生成设计构思（可能需要 30-60 秒）...")
    concept = generate_design_concept(user_input, doc_content)

    print("\n" + "=" * 50)
    print("设计构思")
    print("=" * 50)
    print(concept)
    print("=" * 50 + "\n")

    output_path = session_root / "design_concept.txt"
    output_path.write_text(concept, encoding='utf-8')
    print(f"设计构思已保存到：{output_path}")
    print(f"\n[DESIGN_CONCEPT_OUTPUT]\n{concept}\n[END_DESIGN_CONCEPT_OUTPUT]")


if __name__ == "__main__":
    main()

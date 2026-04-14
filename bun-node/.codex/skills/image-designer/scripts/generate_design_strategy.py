#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_design_strategy.py
第五步：生成设计策略脚本

功能：
- 基于设计构思和设计元素分析文本
- 通过 Qwen 模型生成一份设计策略，包含 4 种不同风格的设计方案

用法:
    python generate_design_strategy.py "<设计构思>" "<设计元素分析>"
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

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent

# 导入工具模块
from session_utils import get_session_root, get_session_subdir
from llm_utils import (
    generate_text_with_messages,
    check_api_key
)


def get_project_root() -> Path:
    """获取当前 session 的工作根目录（而非项目根目录）"""
    return get_session_root()


DESIGN_STRATEGY_SYSTEM_PROMPT = """
【角色设定】：
你是一位资深视觉设计专家，擅长内容如下：
1. 品牌与标识设计，包括：Logo 设计，品牌视觉识别系统，名片、信纸等品牌物料。
2. 营销与广告设计，包括：社交媒体海报与横幅，电商产品主图、详情图，促销广告、活动海报，宣传单页、传单。
3. 创意与艺术设计，包括：插画与概念艺术，IP 形象与吉祥物设计，艺术风格化图像，封面设计（书籍、专辑等）。
4. 图像编辑与处理，包括：图片修改与优化，风格转换（如照片转插画），多图合成，背景替换。
5. 内容创作，包括：社交媒体配图，文章/博客封面图，演示文稿视觉素材，节日贺卡。
"""


def build_design_strategy_messages(concept: str, analysis: str, doc_content: str = None) -> list:
    """构建设计策略的 messages"""
    prompt = f"""
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
{analysis}
"""

    return [
        {"role": "system", "content": DESIGN_STRATEGY_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]


def generate_design_strategy(concept: str, analysis: str, doc_content: str = None) -> str:
    """
    生成设计策略（包含 4 种不同风格方案）

    Args:
        concept: 设计构思
        analysis: 设计元素分析
        doc_content: 文档内容（可选）

    Returns:
        str: 设计策略文本
    """
    messages = build_design_strategy_messages(concept, analysis, doc_content)

    try:
        strategy = generate_text_with_messages(
            messages=messages,
            model="qwen-max-latest",
            temperature=0.8,
            progress_prefix="[设计策略] "
        )
        return strategy

    except Exception as e:
        print(f"生成设计策略时出错：{e}")
        sys.exit(1)


def main():
    # 检查 API Key
    if not check_api_key():
        sys.exit(1)

    # 获取 session 目录
    session_dir = get_project_root()

    # 从文件读取（如果存在）
    concept_path = session_dir / "design_concept.txt"
    analysis_path = session_dir / "reference_images_analysis.txt"
    extracted_text_path = session_dir / "extraced_text.txt"

    # 读取文档内容（如果存在 extraced_text.txt）
    doc_content = ""
    if extracted_text_path.exists():
        print(f"从 {extracted_text_path} 读取文档内容...")
        with open(extracted_text_path, 'r', encoding='utf-8') as f:
            doc_content = f.read()
    # 读取设计构思和分析结果
    if concept_path.exists() and analysis_path.exists():
        print(f"从文件读取设计构思和分析结果...")
        with open(concept_path, 'r', encoding='utf-8') as f:
            concept = f.read()
        with open(analysis_path, 'r', encoding='utf-8') as f:
            analysis = f.read()
    else:
        print("或确保 design_concept.txt 和 reference_images_analysis.txt 存在于项目根目录")
        sys.exit(1)

    print("正在生成设计策略（可能需要 30-60 秒）...")
    strategy = generate_design_strategy(concept, analysis, doc_content)

    # 输出结果
    print("\n" + "=" * 60)
    print("设计策略（4 种风格方案）")
    print("=" * 60)
    print(strategy)
    print("=" * 60 + "\n")

    # 保存到文件
    output_path = session_dir / "design_strategy.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(strategy)

    print(f"设计策略已保存到：{output_path}")

    # 输出策略内容供下一步使用
    print(f"\n[DESIGN_STRATEGY_OUTPUT]\n{strategy}\n[END_DESIGN_STRATEGY_OUTPUT]")


if __name__ == "__main__":
    main()

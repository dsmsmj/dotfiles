#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_design_concept.py
第二步：生成设计构思脚本

功能：
- 合并用户输入要求和提取的文档内容
- 通过 Qwen 模型生成纯文本形式的设计构思

用法:
    python generate_design_concept.py "<合并后的 prompt>"
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


DESIGN_CONCEPT_SYSTEM_PROMPT = """
【角色设定】：
你是一位资深视觉设计专家，擅长内容如下：
1. 品牌与标识设计，包括：Logo 设计，品牌视觉识别系统，名片、信纸等品牌物料。
2. 营销与广告设计，包括：社交媒体海报与横幅，电商产品主图、详情图，促销广告、活动海报，宣传单页、传单。
3. 创意与艺术设计，包括：插画与概念艺术，IP 形象与吉祥物设计，艺术风格化图像，封面设计（书籍、专辑等）。
4. 图像编辑与处理，包括：图片修改与优化，风格转换（如照片转插画），多图合成，背景替换。
5. 内容创作，包括：社交媒体配图，文章/博客封面图，演示文稿视觉素材，节日贺卡。
"""


def build_design_concept_messages(user_input: str, doc_content: str) -> list:
    """构建设计构思的 messages"""
    prompt = f"""
【任务描述】：
请基于【任务要求】以及【材料文本】的内容，遵循以下规则生成一段符合视觉美学的设计构思：
1.如果【材料文本】内容为空，则仅遵循【任务要求】。
2.设计构思中必须根据【任务要求】指明当前任务的具体要求。
3.设计构思中必须指明图片内容所采用的语言，语言优先根据【任务要求】确定，若【任务要求】中未指明所需的语言，则使用与【任务要求】内文本相同的语言。
4.设计构思中必须指明所采用的图片尺寸，必须使用满足【任务要求】的最佳尺寸。
5.设计构思中禁止说明图片的具体内容（包括文字、数据、排版、布局等）。
6.设计构思须内容简洁，采用分段式结构，严禁在提供设计构思之后进行任何形式的询问。
7.生成设计构思时可参考以下设计原则（但不要死板套用）：
	-色彩心理学
	-设计趋势
	-需求分析

【任务要求】：
{user_input}

【材料文本】：
{doc_content}
"""
    return [
        {"role": "system", "content": DESIGN_CONCEPT_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]


def generate_design_concept(user_input: str, doc_content: str) -> str:
    """
    使用 Qwen 模型生成设计构思

    Args:
        user_input: 用户输入
        doc_content: 文档内容

    Returns:
        str: 设计构思文本
    """
    messages = build_design_concept_messages(user_input, doc_content)

    try:
        concept = generate_text_with_messages(
            messages=messages,
            model="qwen-max-latest",
            temperature=0.7,
            progress_prefix="[设计构思] "
        )
        return concept

    except Exception as e:
        print(f"生成设计构思时出错：{e}")
        sys.exit(1)


def main():
    # 检查 API Key
    if not check_api_key():
        sys.exit(1)

    # 获取用户输入的 prompt（如果有）
    user_input = sys.argv[1] if len(sys.argv) >= 2 else ""

    # 尝试从 extraced_text.txt 读取文档内容
    extracted_path = get_project_root() / "extraced_text.txt"
    doc_content = ""

    if extracted_path.exists():
        print(f"\n从 {extracted_path} 读取文档内容...")
        with open(extracted_path, 'r', encoding='utf-8') as f:
            doc_content = f.read()

    print("正在生成设计构思（可能需要 30-60 秒）...")
    concept = generate_design_concept(user_input, doc_content)

    # 输出结果
    print("\n" + "=" * 50)
    print("设计构思")
    print("=" * 50)
    print(concept)
    print("=" * 50 + "\n")

    # 保存到文件
    output_path = get_project_root() / "design_concept.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(concept)

    print(f"设计构思已保存到：{output_path}")

    # 输出构思内容供下一步使用
    print(f"\n[DESIGN_CONCEPT_OUTPUT]\n{concept}\n[END_DESIGN_CONCEPT_OUTPUT]")


if __name__ == "__main__":
    main()

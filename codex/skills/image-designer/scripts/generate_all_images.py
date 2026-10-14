#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_all_images.py
第七步：一次性生成所有 4 张图片

用法:
    python generate_all_images.py
"""

import sys
from pathlib import Path
from typing import Optional

from session_utils import get_session_root
from llm_utils import generate_image_with_minimax, check_api_key
from concurrent_utils import run_concurrent


def _build_image_prompt(design_plan: str) -> str:
    return f"""\
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
{design_plan}"""


def _generate_one(payload: dict) -> Optional[str]:
    enhanced = _build_image_prompt(payload['plan'])
    return generate_image_with_minimax(
        prompt=enhanced,
        image_index=payload['index'],
        save_dir=payload['output_dir'],
    )


def main():
    if not check_api_key():
        sys.exit(1)

    session_root = get_session_root()
    plans_dir = session_root / "design_plans"

    if not plans_dir.exists():
        print("错误：design_plans 文件夹不存在，请先运行 generate_all_design_plans.py")
        sys.exit(1)

    plan_files = sorted(
        f for f in plans_dir.glob("design_plan_*.txt")
        if f.name != "design_plans_merged.txt"
    )

    if not plan_files:
        print("错误：没有找到任何设计计划")
        sys.exit(1)

    output_dir = session_root / "output"
    output_dir.mkdir(exist_ok=True)

    to_generate = []
    for pf in plan_files[:4]:
        idx = int(pf.stem.split('_')[-1])
        existing = output_dir / f"generated_image_{idx}.png"
        if existing.exists():
            print(f"图片 {idx} 已存在，跳过")
            continue
        to_generate.append((idx, {
            'plan': pf.read_text(encoding='utf-8'),
            'index': idx,
            'output_dir': output_dir,
        }))

    if not to_generate:
        print("所有图片已存在，无需生成")
        return

    results = run_concurrent(to_generate, _generate_one, label='图片生成')

    success = sum(1 for _, path in results if path and 'failed' not in str(path).lower())
    print(f"\n{'=' * 60}")
    print(f"图片生成完成！成功：{success}/{len(to_generate)}")
    print("=" * 60)

    if success == 0:
        print("\n请检查 API 状态或设计计划")
        sys.exit(1)

    for idx, path in results:
        if path and 'failed' not in str(path).lower():
            print(f"\n[GENERATED_IMAGE_{idx}]\n{path}\n[END_GENERATED_IMAGE_{idx}]")


if __name__ == "__main__":
    main()

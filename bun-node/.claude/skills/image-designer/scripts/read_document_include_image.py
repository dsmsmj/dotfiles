#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
read_document_include_image.py
第一步：文档内容提取脚本

功能：
- 提取文档中的文字内容
- 提取文档中的图片，并通过 Qwen 视觉模型进行分析
- 将图片分析结果替换至文本中原图片所在位置
- 生成最终的内容文本保存到 extraced_text.txt

用法:
    python read_document_include_image.py <文档路径>
"""

import sys
import os
import io
import asyncio
import re
from pathlib import Path
from typing import List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor

# 设置 UTF-8 编码（解决 Windows 中文乱码问题）
# 使用安全的方式，避免 "I/O operation on closed file" 错误
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
except (AttributeError, io.UnsupportedOperation, ValueError):
    pass  # 如果 reconfigure 失败，使用默认编码

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


def extract_text_from_document(doc_path: str) -> tuple[str, list]:
    """
    从文档中提取文字和图片

    Args:
        doc_path: 文档路径

    Returns:
        tuple: (提取的文本，图片路径列表)
    """
    text_content = ""
    images = []

    ext = Path(doc_path).suffix.lower()

    if ext == '.pdf':
        # PDF 处理
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(doc_path)
            for page_num, page in enumerate(doc):
                # 提取文本
                text = page.get_text()
                text_content += f"\n--- 第{page_num + 1}页 ---\n"
                text_content += text

                # 提取图片
                image_list = page.get_images(full=True)
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]

                    # 保存临时图片到 session 目录
                    session_temp_dir = get_session_subdir('temp_images')
                    temp_img_path = session_temp_dir / f"page_{page_num + 1}_img_{img_index + 1}.{image_ext}"

                    with open(temp_img_path, "wb") as f:
                        f.write(image_bytes)

                    images.append(str(temp_img_path))
                    text_content += f"\n[IMAGE_PLACEHOLDER_{page_num + 1}_{img_index + 1}]\n"

            doc.close()

        except ImportError:
            print("错误：需要安装 PyMuPDF。运行：pip install PyMuPDF")
            sys.exit(1)

    elif ext in ['.docx', '.doc']:
        # Word 文档处理 - 按顺序提取文字和图片
        try:
            from docx import Document

            doc = Document(doc_path)

            # 用于存储提取的图片信息（按提取顺序）
            images_dict = {}  # rId -> {index, path, placeholder}
            image_index = 0

            # 先收集所有图片信息
            for rel in doc.part.rels.values():
                if "image" in rel.target_ref:
                    image_index += 1
                    try:
                        image_bytes = rel.target_part.blob
                        content_type = rel.target_part.content_type
                        image_ext = content_type.split('/')[-1]
                        if image_ext == 'jpeg':
                            image_ext = 'jpg'

                        # 保存临时图片到 session 目录
                        session_temp_dir = get_session_subdir('temp_images')
                        temp_img_path = session_temp_dir / f"word_img_{image_index}.{image_ext}"

                        with open(temp_img_path, "wb") as f:
                            f.write(image_bytes)

                        images_dict[rel.rId] = {
                            'index': image_index,
                            'path': str(temp_img_path),
                            'placeholder': f"\n[IMAGE_PLACEHOLDER_{image_index}]\n"
                        }
                    except Exception as e:
                        print(f"警告：提取图片 {image_index} 失败：{e}")

            # 构建 rId 到 image_info 的映射，用于后续查找
            # 需要跟踪每个图片是否已被插入
            used_images = set()

            def find_image_in_element(element):
                """在 XML 元素中查找图片 blip 的 rId"""
                blip = element.find('.//{http://schemas.openxmlformats.org/drawingml/2006/main}blip')
                if blip is not None:
                    rId = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                    return rId
                return None

            def get_para_text(para):
                """提取段落文本"""
                return ''.join(t.text for t in para.iterchildren('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r') if t.text) or para.text or ''

            def get_cell_text(cell):
                """提取单元格文本"""
                texts = []
                for para in cell:
                    text = get_para_text(para)
                    if text and text.strip():
                        texts.append(text.strip())
                return ' | '.join(texts)

            # 遍历文档主体内容，按顺序获取文字和图片
            text_parts = []
            document_xml = doc._element.body

            for child in document_xml:
                tag_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag

                # 处理段落
                if tag_name == 'p':
                    # 先检查段落中是否有图片
                    rId = find_image_in_element(child)
                    if rId and rId in images_dict and rId not in used_images:
                        img_info = images_dict[rId]
                        used_images.add(rId)
                        text_parts.append(img_info['placeholder'])

                    # 提取段落文本
                    para_text = get_para_text(child)
                    if para_text and para_text.strip():
                        text_parts.append(para_text.strip() + "\n")

                # 处理表格
                elif tag_name == 'tbl':
                    for row in child.iterchildren():
                        row_texts = []
                        for cell in row.iterchildren():
                            # 检查单元格中是否有图片
                            rId = find_image_in_element(cell)
                            if rId and rId in images_dict and rId not in used_images:
                                img_info = images_dict[rId]
                                used_images.add(rId)
                                text_parts.append(img_info['placeholder'])

                            cell_text = get_cell_text(cell)
                            if cell_text:
                                row_texts.append(cell_text)
                        if row_texts:
                            text_parts.append(" | ".join(row_texts) + "\n")

            text_content = "".join(text_parts)

            print(f"Word 文档提取完成，共提取 {len(text_content)} 字符")
            if images_dict:
                print(f"发现 {len(images_dict)} 张图片")

            # 更新 images 列表供后续分析使用（按顺序）
            # 按照 placeholder 中出现的顺序排列图片
            ordered_images = []
            for idx in range(1, len(images_dict) + 1):
                for img_info in images_dict.values():
                    if img_info['index'] == idx:
                        ordered_images.append(img_info['path'])
                        break

            images = ordered_images

        except ImportError:
            print("错误：需要安装 python-docx。运行：pip install python-docx")
            sys.exit(1)
        except Exception as e:
            print(f"读取 Word 文档时出错：{e}")
            # 备用方案：尝试直接使用 zip 解压 docx 并解析 XML
            try:
                import zipfile
                import xml.etree.ElementTree as ET

                with zipfile.ZipFile(doc_path) as z:
                    # 提取文本
                    with z.open('word/document.xml') as f:
                        tree = ET.parse(f)
                        root = tree.getroot()
                        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                        for para in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                            if para.text:
                                text_content += para.text

                    # 提取图片
                    image_index = 0
                    for name in z.namelist():
                        if name.startswith('word/media/') and not name.endswith('/'):
                            try:
                                image_index += 1
                                image_bytes = z.read(name)
                                image_ext = name.split('.')[-1] if '.' in name else 'jpg'

                                # 保存到 session 目录
                                session_temp_dir = get_session_subdir('temp_images')
                                temp_img_path = session_temp_dir / f"word_img_{image_index}.{image_ext}"

                                with open(temp_img_path, "wb") as f:
                                    f.write(image_bytes)

                                images.append(str(temp_img_path))
                                text_content += f"\n[IMAGE_PLACEHOLDER_{image_index}]\n"
                            except Exception as e:
                                print(f"警告：提取图片 {image_index} 失败：{e}")

                print("使用备用方案提取成功")
                if images:
                    print(f"发现 {len(images)} 张图片")
            except Exception as e2:
                print(f"备用方案也失败：{e2}")
                sys.exit(1)

    elif ext in ['.txt', '.md']:
        # 纯文本文件
        with open(doc_path, 'r', encoding='utf-8') as f:
            text_content = f.read()

    else:
        print(f"不支持的文档格式：{ext}")
        sys.exit(1)

    return text_content, images


def analyze_image_with_qwen(image_path: str) -> str:
    """
    使用 Qwen 视觉模型分析图片

    Args:
        image_path: 图片路径

    Returns:
        str: 图片分析结果
    """
    user_prompt = "请用一段有意义的文字描述这张图片，图片中的文字内容必须完整提取并在描述中使用。"
    system_prompt = "你是一个专业的图片分析专家。"

    return analyze_image_with_qwen_vl(
        image_path=image_path,
        user_prompt=user_prompt,
        system_prompt=system_prompt,
        progress_prefix=""
    )


async def analyze_image_async(image_path: str, index: int, semaphore: asyncio.Semaphore,
                               executor: ThreadPoolExecutor) -> Tuple[int, str]:
    """
    异步分析单张图片

    Args:
        image_path: 图片路径
        index: 图片索引（从 1 开始）
        semaphore: 信号量，控制并发数
        executor: 线程池执行器

    Returns:
        Tuple[int, str]: (图片索引，分析结果)
    """
    global _completed_count, _total_count

    async with semaphore:
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                executor,
                lambda: analyze_image_with_qwen(image_path)
            )

            async with _progress_lock:
                _completed_count += 1
                print(f"  ✓ [{_completed_count}/{_total_count}] 图片 {index}: 分析完成")

            return index, result
        except Exception as e:
            async with _progress_lock:
                _completed_count += 1
                print(f"  ✗ [{_completed_count}/{_total_count}] 图片 {index}: 分析失败 - {str(e)}")
            return index, f"[图片分析失败：{str(e)}]"


async def analyze_all_images_async(images: List[str]) -> List[str]:
    """
    异步并发分析所有图片

    Args:
        images: 图片路径列表

    Returns:
        List[str]: 分析结果列表（按原顺序）
    """
    global _completed_count, _total_count
    _completed_count = 0
    _total_count = len(images)

    if _total_count == 0:
        return []

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

    # 创建共享线程池
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_TASKS) as executor:
        tasks = [
            analyze_image_async(img_path, idx + 1, semaphore, executor)
            for idx, img_path in enumerate(images)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # 按原始顺序返回结果
    analyses = [None] * len(images)
    for result in results:
        if isinstance(result, Exception):
            # 异常情况下，放入错误信息（放到末尾）
            analyses.append(f"[分析失败：{str(result)}]")
        else:
            idx, analysis = result
            analyses[idx - 1] = analysis

    # 移除可能存在的 None 值（异常情况下产生）
    analyses = [a for a in analyses if a is not None]

    return analyses


def process_document(doc_path: str) -> str:
    """
    处理文档，提取内容并分析图片（异步并发版本）

    Args:
        doc_path: 文档路径

    Returns:
        str: 处理后的完整文本内容
    """
    print(f"正在处理文档：{doc_path}")

    # 检查 API Key
    if not check_api_key():
        sys.exit(1)

    # 提取文本和图片
    text_content, images = extract_text_from_document(doc_path)

    # 异步并发分析所有图片
    if images:
        print(f"发现 {len(images)} 张图片，开始异步并发分析...")
        print(f"最大并发数：{MAX_CONCURRENT_TASKS}")
        estimated_time = len(images) / MAX_CONCURRENT_TASKS * 1.5
        print(f"预计时间：约 {estimated_time:.1f} 分钟（并行处理，串行时间约 {len(images) * 1.5} 分钟）\n")
        print("分析进度：")

        # 运行异步分析
        analyses = asyncio.run(analyze_all_images_async(images))

        # 检查是否有成功的分析结果
        success_analyses = sum(1 for a in analyses if "分析失败" not in a)
        if success_analyses == 0:
            print(f"\n错误：所有 {len(images)} 张图片分析均失败")
            sys.exit(1)

        # 按顺序替换占位符
        for i, analysis in enumerate(analyses):
            # 跳过分析失败的图片
            if "分析失败" in analysis:
                print(f"  警告：图片 {i + 1} 分析失败，跳过")
                continue

            placeholder_pattern = r'\[IMAGE_PLACEHOLDER_[^\]]+\]'
            match = re.search(placeholder_pattern, text_content)

            if match:
                placeholder = match.group(0)
                replacement = f"\n【图片 {i + 1} 内容】：【{analysis}】\n"
                text_content = text_content.replace(placeholder, replacement, 1)
            else:
                print(f"  警告：未找到占位符，跳过图片 {i + 1}")

    # 保存到 extraced_text.txt（在 session 目录下）
    session_root = get_session_root()
    output_path = session_root / "extraced_text.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text_content)

    print(f"\n提取完成！内容已保存到：{output_path}")
    return text_content


def main():
    if len(sys.argv) < 2:
        print("用法：python read_document_include_image.py <文档路径>")
        print("支持的格式：PDF, DOCX, DOC, TXT, MD")
        sys.exit(1)

    doc_path = sys.argv[1]

    if not os.path.exists(doc_path):
        print(f"错误：文件不存在：{doc_path}")
        sys.exit(1)

    process_document(doc_path)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
read_document_include_image.py
第一步：从 PDF/DOCX/TXT 等文档中提取文字和图片，图片经视觉模型分析后嵌入文本

用法:
    python read_document_include_image.py <文档路径>
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

from session_utils import get_session_root, get_session_subdir
from llm_utils import analyze_image_with_minimax, check_api_key
from concurrent_utils import run_concurrent


# ---------------------------------------------------------------------------
# Document extraction
# ---------------------------------------------------------------------------

def extract_text_from_document(doc_path: str) -> Tuple[str, List[str]]:
    text_content = ""
    images: List[str] = []
    ext = Path(doc_path).suffix.lower()

    if ext == '.pdf':
        text_content, images = _extract_pdf(doc_path)
    elif ext in ('.docx', '.doc'):
        text_content, images = _extract_docx(doc_path)
    elif ext in ('.txt', '.md'):
        text_content = Path(doc_path).read_text(encoding='utf-8')
    else:
        print(f"不支持的文档格式：{ext}")
        sys.exit(1)

    return text_content, images


def _extract_pdf(doc_path: str) -> Tuple[str, List[str]]:
    try:
        import fitz
    except ImportError:
        print("错误：需要安装 PyMuPDF。运行：pip install PyMuPDF")
        sys.exit(1)

    text_content = ""
    images: List[str] = []
    temp_dir = get_session_subdir('temp_images')
    doc = fitz.open(doc_path)

    for page_num, page in enumerate(doc):
        text_content += f"\n--- 第{page_num + 1}页 ---\n{page.get_text()}"
        for img_index, img in enumerate(page.get_images(full=True)):
            base_image = doc.extract_image(img[0])
            img_path = temp_dir / f"page_{page_num + 1}_img_{img_index + 1}.{base_image['ext']}"
            img_path.write_bytes(base_image["image"])
            images.append(str(img_path))
            text_content += f"\n[IMAGE_PLACEHOLDER_{page_num + 1}_{img_index + 1}]\n"

    doc.close()
    return text_content, images


def _extract_docx(doc_path: str) -> Tuple[str, List[str]]:
    try:
        from docx import Document
    except ImportError:
        print("错误：需要安装 python-docx。运行：pip install python-docx")
        sys.exit(1)

    try:
        return _extract_docx_main(doc_path)
    except Exception as e:
        print(f"读取 Word 文档时出错：{e}，尝试备用方案...")
        return _extract_docx_fallback(doc_path)


def _extract_docx_main(doc_path: str) -> Tuple[str, List[str]]:
    from docx import Document

    doc = Document(doc_path)
    temp_dir = get_session_subdir('temp_images')

    images_dict = {}
    image_index = 0
    for rel in doc.part.rels.values():
        if "image" not in rel.target_ref:
            continue
        image_index += 1
        try:
            blob = rel.target_part.blob
            img_ext = rel.target_part.content_type.split('/')[-1]
            if img_ext == 'jpeg':
                img_ext = 'jpg'
            img_path = temp_dir / f"word_img_{image_index}.{img_ext}"
            img_path.write_bytes(blob)
            images_dict[rel.rId] = {
                'index': image_index,
                'path': str(img_path),
                'placeholder': f"\n[IMAGE_PLACEHOLDER_{image_index}]\n",
            }
        except Exception as e:
            print(f"警告：提取图片 {image_index} 失败：{e}")

    used_images: set = set()

    def find_blip_rid(element):
        blip = element.find('.//{http://schemas.openxmlformats.org/drawingml/2006/main}blip')
        if blip is not None:
            return blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
        return None

    def para_text(el):
        return ''.join(
            t.text for t in el.iterchildren('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r')
            if t.text
        ) or el.text or ''

    parts: list = []
    for child in doc._element.body:
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag

        if tag == 'p':
            rid = find_blip_rid(child)
            if rid and rid in images_dict and rid not in used_images:
                used_images.add(rid)
                parts.append(images_dict[rid]['placeholder'])
            text = para_text(child)
            if text.strip():
                parts.append(text.strip() + "\n")

        elif tag == 'tbl':
            for row in child.iterchildren():
                row_texts = []
                for cell in row.iterchildren():
                    rid = find_blip_rid(cell)
                    if rid and rid in images_dict and rid not in used_images:
                        used_images.add(rid)
                        parts.append(images_dict[rid]['placeholder'])
                    texts = []
                    for para in cell:
                        t = para_text(para)
                        if t.strip():
                            texts.append(t.strip())
                    if texts:
                        row_texts.append(' | '.join(texts))
                if row_texts:
                    parts.append(" | ".join(row_texts) + "\n")

    text_content = "".join(parts)
    ordered = []
    for idx in range(1, len(images_dict) + 1):
        for info in images_dict.values():
            if info['index'] == idx:
                ordered.append(info['path'])
                break

    return text_content, ordered


def _extract_docx_fallback(doc_path: str) -> Tuple[str, List[str]]:
    import zipfile
    import xml.etree.ElementTree as ET

    text_content = ""
    images: List[str] = []
    temp_dir = get_session_subdir('temp_images')

    with zipfile.ZipFile(doc_path) as z:
        with z.open('word/document.xml') as f:
            tree = ET.parse(f)
            for node in tree.getroot().iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                if node.text:
                    text_content += node.text

        img_idx = 0
        for name in z.namelist():
            if name.startswith('word/media/') and not name.endswith('/'):
                img_idx += 1
                img_ext = name.rsplit('.', 1)[-1] if '.' in name else 'jpg'
                img_path = temp_dir / f"word_img_{img_idx}.{img_ext}"
                img_path.write_bytes(z.read(name))
                images.append(str(img_path))
                text_content += f"\n[IMAGE_PLACEHOLDER_{img_idx}]\n"

    return text_content, images


# ---------------------------------------------------------------------------
# Image analysis
# ---------------------------------------------------------------------------

def _analyze_doc_image(image_path: str) -> str:
    return analyze_image_with_minimax(
        image_path=image_path,
        user_prompt="请用一段有意义的文字描述这张图片，图片中的文字内容必须完整提取并在描述中使用。",
        system_prompt="你是一个专业的图片分析专家。",
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def process_document(doc_path: str) -> str:
    print(f"正在处理文档：{doc_path}")
    if not check_api_key():
        sys.exit(1)

    text_content, images = extract_text_from_document(doc_path)

    if images:
        print(f"发现 {len(images)} 张图片，开始并发分析...\n")
        items = [(i + 1, img) for i, img in enumerate(images)]
        results = run_concurrent(items, _analyze_doc_image, label='文档图片分析')

        for idx, analysis in results:
            if analysis and '分析失败' not in str(analysis):
                placeholder_pattern = r'\[IMAGE_PLACEHOLDER_[^\]]+\]'
                match = re.search(placeholder_pattern, text_content)
                if match:
                    text_content = text_content.replace(
                        match.group(0),
                        f"\n【图片 {idx} 内容】：【{analysis}】\n",
                        1,
                    )

    output_path = get_session_root() / "extracted_text.txt"
    output_path.write_text(text_content, encoding='utf-8')
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

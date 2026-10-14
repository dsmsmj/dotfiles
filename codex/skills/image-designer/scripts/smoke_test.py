#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
smoke_test.py
快速校验 image-designer 脚本是否可执行。

默认模式（离线）：
- 校验所有脚本可被 Python 编译
- 逐个执行入口脚本，使用可预期失败（缺少 MINIMAX_API_KEY）作为通过条件

--live 模式（联网）：
- 需要真实 MINIMAX_API_KEY
- 仅执行轻量真实调用（simple_t2i）
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

SCRIPT_DIR = Path(__file__).parent
CORE_SCRIPTS = [
    'read_document_include_image.py',
    'generate_design_concept.py',
    'search_reference_images.py',
    'analyze_reference_images.py',
    'generate_design_strategy.py',
    'generate_all_design_plans.py',
    'generate_all_images.py',
    'edit_images.py',
    'simple_t2i.py',
]


@dataclass
class Case:
    name: str
    cmd: list[str]
    expect_contains: str


def run(cmd: Sequence[str], env: dict[str, str], timeout: int) -> tuple[int, str]:
    proc = subprocess.run(
        list(cmd),
        cwd=str(SCRIPT_DIR),
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
        encoding='utf-8',
        errors='replace',
    )
    output = f'{proc.stdout}\n{proc.stderr}'.strip()
    return proc.returncode, output


def compile_all(py: str) -> tuple[bool, str]:
    cmd = [py, '-m', 'py_compile']
    for script in CORE_SCRIPTS:
        cmd.append(str(SCRIPT_DIR / script))
    code, output = run(cmd, os.environ.copy(), timeout=60)
    return code == 0, output


def write_fixtures(session_root: Path) -> tuple[Path, Path]:
    session_root.mkdir(parents=True, exist_ok=True)
    (session_root / 'design_concept.txt').write_text('测试构思内容', encoding='utf-8')
    (session_root / 'reference_images_analysis.txt').write_text('测试分析内容', encoding='utf-8')
    (session_root / 'design_strategy.txt').write_text(
        '方案一：清新风|||方案二：极简风|||方案三：科技风|||方案四：复古风',
        encoding='utf-8',
    )

    plans = session_root / 'design_plans'
    plans.mkdir(parents=True, exist_ok=True)
    for i in range(1, 5):
        (plans / f'design_plan_{i}.txt').write_text(f'设计计划 {i}', encoding='utf-8')

    ref = session_root / 'reference_images'
    ref.mkdir(parents=True, exist_ok=True)
    png_bytes = base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO7Xx5QAAAAASUVORK5CYII='
    )
    test_image = ref / 'sample.png'
    test_image.write_bytes(png_bytes)

    test_doc = session_root / 'smoke_doc.txt'
    test_doc.write_text('这是一份 smoke test 文档。', encoding='utf-8')
    return test_doc, test_image


def build_cases(py: str, test_doc: Path, test_image: Path) -> list[Case]:
    return [
        Case('read_document_include_image', [py, 'read_document_include_image.py', str(test_doc)], 'MINIMAX_API_KEY 未设置'),
        Case('generate_design_concept', [py, 'generate_design_concept.py', '做一张海报'], 'MINIMAX_API_KEY 未设置'),
        Case('search_reference_images', [py, 'search_reference_images.py'], 'MINIMAX_API_KEY 未设置'),
        Case('analyze_reference_images', [py, 'analyze_reference_images.py'], 'MINIMAX_API_KEY 未设置'),
        Case('generate_design_strategy', [py, 'generate_design_strategy.py'], 'MINIMAX_API_KEY 未设置'),
        Case('generate_all_design_plans', [py, 'generate_all_design_plans.py'], 'MINIMAX_API_KEY 未设置'),
        Case('generate_all_images', [py, 'generate_all_images.py'], 'MINIMAX_API_KEY 未设置'),
        Case('edit_images', [py, 'edit_images.py', str(test_image), '整体风格更柔和'], 'MINIMAX_API_KEY 未设置'),
        Case('simple_t2i', [py, 'simple_t2i.py', '一只在月光下的白猫'], 'MINIMAX_API_KEY 未设置'),
    ]


def run_offline(py: str, timeout: int) -> int:
    ok_compile, compile_output = compile_all(py)
    if not ok_compile:
        print('[FAIL] py_compile 失败')
        print(compile_output)
        return 1
    print('[PASS] py_compile 通过')

    with tempfile.TemporaryDirectory(prefix='image-designer-smoke-') as tmp:
        tmp_path = Path(tmp)
        session_root = tmp_path / 'sessions' / 'smoke-test'
        test_doc, test_image = write_fixtures(session_root)

        env = os.environ.copy()
        env['ACPX_DATA_ROOT'] = str(tmp_path)
        env['ACPX_QUEUE_OWNER_PAYLOAD'] = json.dumps({'acp_session_id': 'smoke-test'})
        env.pop('MINIMAX_API_KEY', None)

        failed = 0
        for case in build_cases(py, test_doc, test_image):
            code, output = run(case.cmd, env, timeout)
            matched = case.expect_contains in output
            has_traceback = 'Traceback (most recent call last)' in output
            passed = code != 0 and matched and not has_traceback

            if passed:
                print(f'[PASS] {case.name}')
            else:
                failed += 1
                print(f'[FAIL] {case.name} (exit={code})')
                print(output[:1200] if output else '<no output>')

        return 1 if failed else 0


def run_live(py: str, timeout: int) -> int:
    if not os.getenv('MINIMAX_API_KEY'):
        print('[FAIL] --live 模式需要设置 MINIMAX_API_KEY')
        return 1

    with tempfile.TemporaryDirectory(prefix='image-designer-live-') as tmp:
        tmp_path = Path(tmp)
        env = os.environ.copy()
        env['ACPX_DATA_ROOT'] = str(tmp_path)
        env['ACPX_QUEUE_OWNER_PAYLOAD'] = json.dumps({'acp_session_id': 'live-smoke'})
        cmd = [py, 'simple_t2i.py', '一张极简风格的测试图，白底黑线条']
        code, output = run(cmd, env, timeout)
        has_success_tag = '[GENERATED_IMAGE_1]' in output
        if code == 0 and has_success_tag:
            print('[PASS] live simple_t2i 通过')
            return 0
        print(f'[FAIL] live simple_t2i 失败 (exit={code})')
        print(output[:1200] if output else '<no output>')
        return 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='image-designer 脚本冒烟测试')
    parser.add_argument('--python', default=sys.executable, help='Python 可执行文件路径')
    parser.add_argument('--timeout', type=int, default=60, help='单脚本超时（秒）')
    parser.add_argument('--live', action='store_true', help='执行真实 API 连通性测试')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.live:
        return run_live(args.python, args.timeout)
    return run_offline(args.python, args.timeout)


if __name__ == '__main__':
    raise SystemExit(main())

# -*- coding: utf-8 -*-
"""
concurrent_utils.py
通用并发执行工具 - 替代各脚本中重复的 asyncio+ThreadPoolExecutor 样板
"""

import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, List, Optional, Tuple, TypeVar

from llm_utils import MAX_CONCURRENT_TASKS

T = TypeVar('T')


def run_concurrent(
    items: List[Tuple[int, Any]],
    worker_fn: Callable[[Any], T],
    label: str = '',
    max_workers: int = MAX_CONCURRENT_TASKS,
) -> List[Tuple[int, Optional[T]]]:
    """
    并发执行 worker_fn 并打印进度。

    Args:
        items: [(index, payload), ...] — index 用于结果排序和日志
        worker_fn: 接受 payload、返回结果的同步函数
        label: 日志前缀，如 '图片分析'
        max_workers: 最大并发数

    Returns:
        [(index, result_or_None), ...] 按 index 排序
    """
    total = len(items)
    completed = 0
    lock = threading.Lock()
    results: List[Tuple[int, Optional[T]]] = []

    prefix = f'[{label}] ' if label else ''
    print(f'{prefix}共 {total} 项，最大并发 {max_workers}', file=sys.stderr)

    def _wrapped(idx: int, payload: Any) -> Tuple[int, Optional[T]]:
        nonlocal completed
        try:
            result = worker_fn(payload)
            with lock:
                completed += 1
                print(f'  ✓ [{completed}/{total}] {prefix}{idx}: 完成', file=sys.stderr)
            return idx, result
        except Exception as e:
            with lock:
                completed += 1
                print(f'  ✗ [{completed}/{total}] {prefix}{idx}: {e}', file=sys.stderr)
            return idx, None

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_wrapped, idx, payload): idx
            for idx, payload in items
        }
        for future in as_completed(futures):
            results.append(future.result())

    results.sort(key=lambda r: r[0])
    return results

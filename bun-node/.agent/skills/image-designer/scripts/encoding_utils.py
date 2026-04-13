# -*- coding: utf-8 -*-
"""
encoding_utils.py
Windows 环境下 Python 脚本的 UTF-8 编码设置工具

功能：
- 安全地设置标准输出/错误为 UTF-8 编码
- 兼容多种执行环境（命令行、subprocess、IDE 等）
- 避免 "I/O operation on closed file" 错误
"""

import sys
import io
import os


def setup_utf8_encoding():
    """
    安全地设置标准输出和错误为 UTF-8 编码

    说明：
    - 在 Windows 上，Python 默认使用系统编码（通常是 GBK）
    - 这会导致中文输出乱码
    - 本函数尝试多种方法设置 UTF-8，并安全处理各种异常情况

    使用方法：
    在每个需要输出中文的脚本开头调用：
        from encoding_utils import setup_utf8_encoding
        setup_utf8_encoding()
    """

    # 方法 1：尝试使用 PYTHONIOENCODING 环境变量（最安全）
    # 这个方法在 Python 启动时生效，但我们可以在运行时检查
    if os.environ.get('PYTHONIOENCODING') == 'utf-8':
        return  # 已经设置好了

    # 方法 2：尝试 reconfigure（Python 3.7+）
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
        return
    except (AttributeError, io.UnsupportedOperation, ValueError):
        pass  # reconfigure 不可用或失败

    # 方法 3：尝试包装 TextIOWrapper（仅在 buffer 可用且未关闭时）
    try:
        if (hasattr(sys.stdout, 'buffer') and
            not getattr(sys.stdout, 'closed', False) and
            hasattr(sys.stdout.buffer, 'write')):
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer,
                encoding='utf-8',
                line_buffering=True
            )
    except (AttributeError, io.UnsupportedOperation, ValueError):
        pass

    try:
        if (hasattr(sys.stderr, 'buffer') and
            not getattr(sys.stderr, 'closed', False) and
            hasattr(sys.stderr.buffer, 'write')):
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer,
                encoding='utf-8',
                line_buffering=True
            )
    except (AttributeError, io.UnsupportedOperation, ValueError):
        pass

    # 方法 4：如果以上都失败，设置环境变量供子进程使用
    os.environ['PYTHONIOENCODING'] = 'utf-8'


def safe_print(*args, **kwargs):
    """
    安全的 print 函数，自动处理编码问题

    用法：替代内置 print，确保中文正常输出
    """
    try:
        # 确保 kwargs 中有 encoding
        if 'file' not in kwargs:
            # 默认输出到 stdout
            print(*args, **kwargs)
        else:
            print(*args, **kwargs)
    except (UnicodeEncodeError, UnicodeDecodeError):
        # 如果编码失败，尝试使用 errors='replace'
        safe_args = [str(arg).encode('utf-8', errors='replace').decode('utf-8', errors='replace')
                     for arg in args]
        print(*safe_args, **kwargs)


def get_system_encoding():
    """获取当前系统编码"""
    return sys.stdout.encoding if hasattr(sys.stdout, 'encoding') else 'unknown'

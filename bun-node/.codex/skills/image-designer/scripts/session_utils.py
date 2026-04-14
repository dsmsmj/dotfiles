# -*- coding: utf-8 -*-
"""
session_utils.py
Session 管理工具模块

功能：
- 从 ACPX_QUEUE_OWNER_PAYLOAD 环境变量中提取 sessionId
- 获取 session 工作目录路径（项目根目录/{session_name}/）
- 确保 session 目录存在
"""

import os
from pathlib import Path


def get_session_id() -> str:
    """
    获取当前会话 ID

    仅从 ACPX_QUEUE_OWNER_PAYLOAD 环境变量中提取 sessionId

    Returns:
        str: 会话 ID
    """
    # 从 acpx 的 session 信息中提取 sessionId
    acpx_payload = os.environ.get('ACPX_QUEUE_OWNER_PAYLOAD')
    if acpx_payload:
        import json
        try:
            payload = json.loads(acpx_payload)
            session_id = payload.get('sessionId')
            if session_id:
                return session_id
        except (json.JSONDecodeError, TypeError):
            pass

    # 如果无法获取 sessionId，返回 default
    return 'default'


def get_project_root() -> Path:
    """
    获取项目根目录（.claude/skills/image-designer/scripts/ 向上 5 层）

    Returns:
        Path: 项目根目录绝对路径
    """
    return Path(__file__).parent.parent.parent.parent.parent


def get_session_root() -> Path:
    """
    获取当前 session 的工作根目录

    路径格式：{项目根目录}/{session_name}/
    每个不同的 session 在根目录下有独立的文件夹

    Returns:
        Path: session 工作根目录绝对路径
    """
    session_id = get_session_id()
    project_root = get_project_root()
    session_root = project_root / session_id

    # 确保 session 目录存在
    session_root.mkdir(parents=True, exist_ok=True)

    return session_root


def get_session_subdir(subdir_name: str) -> Path:
    """
    获取 session 下的子目录路径

    Args:
        subdir_name: 子目录名称（如 'output', 'reference_images', 'design_plans'）

    Returns:
        Path: session 子目录绝对路径（{项目根目录}/{session_name}/{subdir_name}/）
    """
    session_root = get_session_root()
    subdir_path = session_root / subdir_name

    # 确保子目录存在
    subdir_path.mkdir(parents=True, exist_ok=True)

    return subdir_path

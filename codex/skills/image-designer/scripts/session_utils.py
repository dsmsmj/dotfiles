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

UUID_V4_LIKE = r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'


def _is_uuid_like(value: str) -> bool:
    import re

    return bool(re.match(UUID_V4_LIKE, value.strip(), flags=re.IGNORECASE))


def get_sandbox_id() -> str:
    """
    获取当前 Sandbox ID (默认兼容从 Session 机制中获取)

    从 ACPX_QUEUE_OWNER_PAYLOAD 中读取 acp_session_id（运行时动态注入，每个 session 唯一）。
    仅接受 UUID，未注入或无效时返回 'default'。

    Returns:
        str: 会话 ID
    """
    import json

    acpx_payload = os.environ.get('ACPX_QUEUE_OWNER_PAYLOAD')
    if acpx_payload:
        try:
            payload = json.loads(acpx_payload)
            candidates = [
                payload.get('acp_session_id'),
                payload.get('sessionId'),
                payload.get('acpx_record_id'),
            ]
            normalized = [
                str(item).strip() for item in candidates
                if isinstance(item, str) and item.strip()
            ]
            for session_id in normalized:
                if _is_uuid_like(session_id):
                    return session_id
        except (json.JSONDecodeError, TypeError):
            pass

    env_candidates = [
        os.environ.get('ACP_SESSION_ID'),
        os.environ.get('SESSION_ID'),
        os.environ.get('ACPX_RECORD_ID'),
    ]
    normalized_env = [item.strip() for item in env_candidates if isinstance(item, str) and item.strip()]
    for session_id in normalized_env:
        if _is_uuid_like(session_id):
            return session_id
    return 'default'

get_session_id = get_sandbox_id


def get_project_root() -> Path:
    """
    获取项目根目录（.claude/skills/image-designer/scripts/ 向上 5 层）

    Returns:
        Path: 项目根目录绝对路径
    """
    return Path(__file__).parent.parent.parent.parent.parent


def get_data_root() -> Path:
    """
    获取数据根目录。

    优先读取 ACPX_DATA_ROOT 环境变量（ACP 运行时注入），
    回退到 {project_root}/data，与 runtime.ts 中 DATA_ROOT 保持一致。

    Returns:
        Path: 数据根目录绝对路径
    """
    acpx_data_root = os.environ.get('ACPX_DATA_ROOT')
    if acpx_data_root:
        return Path(acpx_data_root)
    return get_project_root() / 'data'


def get_acpx_root() -> Path:
    """
    获取 .acpx 根目录。

    兼容两种输入：
    - ACPX_DATA_ROOT / 默认 data 根目录（需要补上 .acpx）
    - 已经指向 .acpx 的路径（直接使用）

    Returns:
        Path: .acpx 根目录绝对路径
    """
    data_root = get_data_root()
    if data_root.name == '.acpx':
        return data_root
    return data_root / '.acpx'


def get_session_root() -> Path:
    """
    获取当前 session 的工作根目录（用于图片设计产物落盘），引入沙盒(sandbox)机制。

    路径格式：{data_root}/.acpx/sandbox/{sandbox_id}/
    与当前 ACPX 输出目录策略保持兼容并演进为沙盒。

    Returns:
        Path: sandbox / session 工作根目录绝对路径
    """
    sandbox_id = get_sandbox_id()
    session_root = get_acpx_root() / 'sandbox' / sandbox_id

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

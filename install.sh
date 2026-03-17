#!/bin/bash

# 定义 dotfiles 仓库路径
dotfiles_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "开始安装 dotfiles..."

# 备份现有配置文件并创建符号链接
link_file () {
    local source="$1"
    local target="$2"

    # 确保目标目录存在
    local target_dir=$(dirname "$target")
    mkdir -p "$target_dir"

    if [ -f "$target" ] || [ -d "$target" ]; then
        echo "备份现有文件/目录: ${target} -> ${target}.bak"
        mv "$target" "${target}.bak"
    fi

    echo "创建符号链接: ${source} -> ${target}"
    ln -sf "$source" "$target"
}

# Git 配置
link_file "${dotfiles_dir}/git/.gitconfig" "${HOME}/.gitconfig"

# Node/npm 配置
link_file "${dotfiles_dir}/node/.npmrc" "${HOME}/.npmrc"

# SSH 配置
link_file "${dotfiles_dir}/ssh/config" "${HOME}/.ssh/config"
chmod 600 "${HOME}/.ssh/config" # SSH config 文件需要严格权限

# 根据操作系统判断 VSCode 和 Cursor AI 的配置路径
if [[ "$OSTYPE" == "darwin" ]]; then
    # macOS
    VSCODE_CONFIG_DIR="${HOME}/Library/Application Support/Code/User"
    CURSOR_CONFIG_DIR="${HOME}/Library/Application Support/Cursor/User"
elif [[ "$OSTYPE" == "linux-gnu" ]]; then
    # Linux
    VSCODE_CONFIG_DIR="${HOME}/.config/Code/User"
    CURSOR_CONFIG_DIR="${HOME}/.config/Cursor/User"
else
    echo "警告: 未知操作系统类型 '${OSTYPE}'。VSCode 和 Cursor AI 配置可能无法正确安装。"
    VSCODE_CONFIG_DIR="${HOME}/.config/Code/User"
    CURSOR_CONFIG_DIR="${HOME}/.config/Cursor/User"
fi

# VSCode 配置
link_file "${dotfiles_dir}/vscode/settings.json" "${VSCODE_CONFIG_DIR}/settings.json"

# Cursor AI 配置
link_file "${dotfiles_dir}/cursor/settings.json" "${CURSOR_CONFIG_DIR}/settings.json"

echo "dotfiles 安装完成！"

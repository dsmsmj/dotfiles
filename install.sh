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

# WSL：编辑器跑在 Windows 侧，这里只装 shell 和系统配置
if grep -qi microsoft /proc/version 2>/dev/null; then
    echo "检测到 WSL"
    line="[ -f \"${dotfiles_dir}/wsl/ubuntu/bashrc.custom.sh\" ] && . \"${dotfiles_dir}/wsl/ubuntu/bashrc.custom.sh\""
    grep -qF "wsl/ubuntu/bashrc.custom.sh" "${HOME}/.bashrc" 2>/dev/null || echo "$line" >> "${HOME}/.bashrc"
    if ! cmp -s "${dotfiles_dir}/wsl/ubuntu/wsl.conf" /etc/wsl.conf; then
        echo "更新 /etc/wsl.conf（需要 sudo，之后在 PowerShell 执行 wsl --shutdown 生效）"
        sudo cp "${dotfiles_dir}/wsl/ubuntu/wsl.conf" /etc/wsl.conf
    fi
    echo "apt 包清单：wsl/ubuntu/apt-manual.txt（需要时手动安装）"
    [ -f "${HOME}/.gitconfig.local" ] || cp "${dotfiles_dir}/git/.gitconfig.local.example" "${HOME}/.gitconfig.local"
    echo "dotfiles 安装完成！"
    exit 0
fi

# 根据操作系统判断 VSCode 和 Cursor AI 的配置路径
if [[ "$OSTYPE" == darwin* ]]; then
    # macOS
    VSCODE_CONFIG_DIR="${HOME}/Library/Application Support/Code/User"
    CURSOR_CONFIG_DIR="${HOME}/Library/Application Support/Cursor/User"
elif [[ "$OSTYPE" == linux* ]]; then
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

link_file "${dotfiles_dir}/vscode/keybindings.json" "${VSCODE_CONFIG_DIR}/keybindings.json"
link_file "${dotfiles_dir}/vscode/snippets" "${VSCODE_CONFIG_DIR}/snippets"

# Cursor AI 配置
link_file "${dotfiles_dir}/cursor/settings.json" "${CURSOR_CONFIG_DIR}/settings.json"
link_file "${dotfiles_dir}/vscode/snippets" "${CURSOR_CONFIG_DIR}/snippets"

# 本机私有配置模板（只在不存在时生成，不覆盖）
[ -f "${HOME}/.gitconfig.local" ] || cp "${dotfiles_dir}/git/.gitconfig.local.example" "${HOME}/.gitconfig.local"
if [ ! -f "${HOME}/.m2/settings.xml" ]; then
    mkdir -p "${HOME}/.m2" && cp "${dotfiles_dir}/maven/settings.template.xml" "${HOME}/.m2/settings.xml"
fi

echo "dotfiles 安装完成！"

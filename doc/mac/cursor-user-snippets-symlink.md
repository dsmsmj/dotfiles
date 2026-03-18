# Cursor（macOS）用户配置软链接（snippets/settings/keybindings）

本文记录在 macOS 上将 Cursor 的用户配置目录通过**软链接**指向本仓库（dotfiles）的做法，包含常见报错原因与修复步骤。

## 背景与目录约定

Cursor 的用户数据通常在：

- `~/Library/Application Support/Cursor/User/`

其中常用的 3 类文件/目录：

- `settings.json`
- `keybindings.json`
- `snippets/`（用户代码片段目录）

本仓库中（以当前仓库为例）：

- VS Code/Cursor 相关配置在 `vscode/` 下
- snippets 在 `vscode/snippets/` 下

## 常见坑：为什么 `mkdir -p .../snippets` 会失败

如果你看到类似错误：

```bash
mkdir: /Users/<you>/Library/Application Support/Cursor/User/snippets: No such file or directory
```

最常见原因不是权限，而是：

- `~/Library/Application Support/Cursor/User/snippets` **已经存在**，但它是一个**指向不存在目标的软链接**（坏链接）
- 或者 `Cursor/User/` 下存在同名的**普通文件**占位，导致无法创建目录

验证方式：

```bash
ls -la "$HOME/Library/Application Support/Cursor/User" | sed -n '1,200p'
ls -la "$HOME/Library/Application Support/Cursor/User/snippets"
```

如果 `snippets -> /path/does/not/exist`，就属于坏链接情况，必须先修复链接目标或重建链接。

## 推荐做法：把 Cursor 配置软链到本仓库

下面命令会把 Cursor 的 `snippets/settings/keybindings` 软链到本仓库的 `vscode/` 目录结构。

> 注意：会覆盖 Cursor/User 下同名路径（通过 `rm -f` 删除旧链接/旧文件），不会删除你的仓库内容。

```bash
USER_DIR="$HOME/Library/Application Support/Cursor/User"
DOTFILES_DIR="/Users/muji/dev_config/dotfiles"

# 1) snippets：删除旧的 snippets（文件或旧链接），重新链接到仓库目录
rm -f "$USER_DIR/snippets"
ln -s "$DOTFILES_DIR/vscode/snippets" "$USER_DIR/snippets"

# 2) settings / keybindings：同理重新链接
rm -f "$USER_DIR/settings.json" "$USER_DIR/keybindings.json"
ln -s "$DOTFILES_DIR/vscode/settings.json" "$USER_DIR/settings.json"
ln -s "$DOTFILES_DIR/vscode/keybindings.json" "$USER_DIR/keybindings.json"
```

## 验证

```bash
ls -la "$HOME/Library/Application Support/Cursor/User/settings.json"
ls -la "$HOME/Library/Application Support/Cursor/User/keybindings.json"
ls -la "$HOME/Library/Application Support/Cursor/User/snippets"
```

预期输出里应显示 `->` 指向本仓库对应路径，例如：

- `snippets -> /Users/muji/dev_config/dotfiles/vscode/snippets`

## 额外建议：避免使用 `cursor/` 作为真实目录

如果仓库里存在名为 `cursor` 的路径且它是一个指向其它系统/机器的链接（例如 Windows 路径），建议不要让它成为 Cursor/User 的软链目标；更稳妥的做法是把 Cursor 相关配置统一放到 `vscode/`（或一个明确的 `cursor/` 实体目录）中，并保证软链目标在当前机器上真实存在。


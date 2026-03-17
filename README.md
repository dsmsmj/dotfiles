# Dotfiles

这是一个用于管理我的编程环境配置文件的仓库。它包含了 VSCode、Git、Node/npm、SSH 和 Cursor AI 的配置，以及一个用于自动安装这些配置的脚本。

## 仓库结构

```
.dotfiles/
├── .github/              # GitHub Actions 工作流
│   └── workflows/
│       └── main.yml
├── cursor/               # Cursor AI 配置
│   └── settings.json
├── git/                  # Git 配置
│   └── .gitconfig
├── node/                 # Node.js/npm 配置
│   └── .npmrc
├── ssh/                  # SSH 配置
│   └── config
├── vscode/               # VSCode 配置
│   └── settings.json
├── install.sh            # 自动安装脚本
└── README.md
```

## 安装

### 1. 克隆仓库

首先，将此仓库克隆到你的本地机器上：

```bash
git clone git@github.com:YourUsername/dotfiles.git ~/.dotfiles
```

### 2. 运行安装脚本

进入克隆的目录并运行 `install.sh` 脚本。这个脚本会将仓库中的配置文件软链接到你的家目录或相应的配置目录，并备份任何现有的同名文件。

```bash
cd ~/.dotfiles
./install.sh
```

**注意：**

*   脚本会备份你现有的配置文件（如果存在），备份文件会以 `.bak` 结尾。
*   SSH 配置文件 (`~/.ssh/config`) 会被设置为 `600` 权限，这是 SSH 客户端的要求。
*   `install.sh` 脚本现在支持 macOS 和 Linux 系统，会自动识别操作系统并链接到正确的配置路径。

### 一键安装 (适用于新机器)

你也可以使用以下命令，在新机器上直接克隆并运行安装脚本：

```bash
git clone https://github.com/YourUsername/dotfiles.git ~/.dotfiles && ~/.dotfiles/install.sh
```

请将 `YourUsername` 替换为你的 GitHub 用户名。

## 配置说明

### Git

*   `.gitconfig`: 包含了你的 Git 用户名、邮箱、常用的别名和默认分支设置。请根据你的实际情况修改 `user.name` 和 `user.email`。

### Node.js / npm

*   `.npmrc`: 配置了 npm 的注册表地址。默认指向官方 npm 注册表。

### SSH

*   `config`: SSH 客户端的配置文件。你可以在这里添加你的 SSH 主机别名、身份文件路径等。例如，用于 GitHub 的配置。

### VSCode

*   `settings.json`: VSCode 的用户设置。包含了字体大小、Tab 宽度、自动保存、主题、终端配置、Git 自动拉取和保存时格式化等设置。

### Cursor AI

*   `settings.json`: Cursor AI 的用户设置。与 VSCode 设置类似，并额外配置了 `cursor.chat.preferredModel` 为 `gpt-4`。

## GitHub Actions

仓库中包含了 `.github/workflows/main.yml` 文件，它定义了一个 GitHub Actions 工作流。这个工作流会在每次 `push` 或 `pull_request` 到仓库时运行，以验证 `install.sh` 脚本是否能成功执行，并检查关键配置文件的内容是否符合预期。这有助于确保你的 dotfiles 始终保持可用和正确。

## 自定义

你可以根据自己的需求修改仓库中的任何配置文件。修改后，重新运行 `install.sh` 脚本即可更新你的系统配置。

## 贡献

欢迎通过 Pull Request 提交改进或建议。

## 许可证

本项目采用 MIT 许可证。

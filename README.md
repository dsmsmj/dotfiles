# Dotfiles

这是一个用于管理我的编程环境配置文件的仓库。它包含了 VSCode、Git、Node/npm、SSH 和 Cursor AI 的配置，以及一个用于自动安装这些配置的脚本。

## 仓库结构

```
.dotfiles/
├── .github/              # GitHub Actions 工作流
│   └── workflows/
│       └── main.yml
├── cursor/               # Cursor AI 配置
│   ├── settings.json
│   └── extensions.txt
├── git/                  # Git 配置
│   ├── .gitconfig
│   └── .gitconfig.local.example
├── node/                 # Node.js/npm 配置
│   └── .npmrc
├── ssh/                  # SSH 配置
│   └── config
├── vscode/               # VSCode 配置
│   ├── settings.json
│   ├── keybindings.json
│   ├── snippets/
│   └── extensions.txt    # 扩展清单
├── maven/                # Maven settings 模板（无密码）
├── wsl/                  # .wslconfig（Windows 侧）+ ubuntu/（WSL 内的 bashrc、wsl.conf、apt 清单）
├── install.sh            # macOS / Linux 安装脚本
├── install.ps1           # Windows 安装脚本
├── windows-terminal/     # Windows Terminal 设置
├── codex/                # Codex 配置 / rules / skills
├── agents/               # ~/.agents skills 的 lock 文件
└── README.md
```

## 安装

### 1. 克隆仓库

首先，将此仓库克隆到你的本地机器上：

```bash
git clone git@github.com:dsmsmj/dotfiles.git ~/.dotfiles
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
git clone https://github.com/dsmsmj/dotfiles.git ~/.dotfiles && ~/.dotfiles/install.sh
```

### Windows

```powershell
git clone https://github.com/dsmsmj/dotfiles.git $HOME\dotfiles
powershell -ExecutionPolicy Bypass -File $HOME\dotfiles\install.ps1 -InstallExtensions
```

创建符号链接需要管理员 PowerShell，或在「设置 → 系统 → 开发者选项」里打开开发者模式。

### WSL（Ubuntu）

在 WSL 里：

```bash
git clone https://github.com/dsmsmj/dotfiles.git ~/dotfiles && ~/dotfiles/install.sh
```

会链接 `.gitconfig`、`.npmrc`、`.ssh/config`，在 `~/.bashrc` 末尾引入 `wsl/ubuntu/bashrc.custom.sh`（代理、PATH），并同步 `/etc/wsl.conf`（开启 systemd）。apt 包清单在 `wsl/ubuntu/apt-manual.txt`。Windows 侧的 `.wslconfig`（`networkingMode=mirrored`）由 `install.ps1` 负责。

### AI 工具配置

| 内容 | 仓库位置 | 安装方式 |
|---|---|---|
| Cursor 规则、developer-context | `.cursor/rules`、`.cursor/developer-context` | `install.ps1` 链接到 `~/.cursor` |
| Cursor 自写 skills、`mcp.json` | `.cursor/skills/*`、`.cursor/mcp.json` | 缺失时复制 |
| Cursor 第三方 skills（frontend-design 等） | `.cursor/skills/skills-lock.json` | 按 lock 里的来源重新装 |
| Codex 配置、rules、自写 skills | `codex/` | 缺失时复制（image-designer 需自己建 `.env`，见 `.env.example`） |
| `~/.agents/skills`（mattpocock、vercel-labs 两套） | `agents/.skill-lock.json` | 用 skills CLI 按 lock 重装 |
| Windows Terminal | `windows-terminal/settings.json` | `install.ps1` 链接 |

### 不进仓库的东西（仓库是公开的）

| 内容 | 放哪 |
|---|---|
| 公司 Git 身份、`safe.directory` | `~/.gitconfig.local`（模板：`git/.gitconfig.local.example`） |
| Maven 私服地址和账号 | `~/.m2/settings.xml`（模板：`maven/settings.template.xml`） |
| Claude Code / 各种 API Key、`claudeCode.environmentVariables` | 只放本机，换机后重新申请 |
| SSH 私钥 | 新机器重新生成，再把公钥加到 GitHub / Gitee |
| 公司专用 skill（如 iconfont） | 公司仓库或私有备份 |
| 各项目的 `.env`、`.env.private` | 私有备份（密码管理器 / 公司网盘） |

## 配置说明

## 环境搭建手册（doc）

总入口（装机顺序 + 文档索引）：`doc/README.md`

### Windows

- `doc/windows/nvm.md`：Node.js 版本管理（nvm-windows）
- `doc/windows/bun.md`：Bun 安装与使用
- `doc/windows/yarn.md`：Yarn 安装与使用（Corepack）
- `doc/windows/pnpm.md`：pnpm 安装与使用（Corepack）
- `doc/windows/docker.md`：Docker Desktop + WSL2 安装与常见坑
- `doc/windows/maven.md`：Maven 安装与 JAVA_HOME 配置
- `doc/windows/git-ssh.md`：Git SSH（生成 Key / 配置远端）

### macOS

- `doc/mac/nvm.md`：Node.js 版本管理（nvm）
- `doc/mac/bun.md`：Bun 安装与使用
- `doc/mac/yarn.md`：Yarn 安装与使用（Corepack）
- `doc/mac/pnpm.md`：pnpm 安装与使用（Corepack）
- `doc/mac/docker.md`：Docker 安装与使用（Docker Desktop / Colima）
- `doc/mac/maven.md`：Maven 安装与使用
- `doc/mac/git-ssh.md`：Git SSH（生成 Key / 配置远端）

### Git

*   `.gitconfig`: 个人身份、常用别名、默认分支、`core.longpaths`。末尾 `include` 了 `~/.gitconfig.local`，公司身份等机器相关配置写在那里。

### Node.js / npm

*   `.npmrc`: 配置了 npm 的注册表地址。默认指向官方 npm 注册表。
*   `npm-globals.txt`: 全局 npm 包清单，安装：`npm i -g $(grep -v '^#' node/npm-globals.txt)`
*   Windows 版本管理（nvm-windows）：见 `doc/windows/nvm.md`

### SSH

*   `config`: SSH 客户端的配置文件。你可以在这里添加你的 SSH 主机别名、身份文件路径等。例如，用于 GitHub 的配置。

### VSCode

*   `settings.json` / `keybindings.json` / `snippets/`: 用户设置、快捷键、代码片段（Cursor 共用同一份 snippets）。
*   `extensions.txt`: 扩展清单，`install.ps1 -InstallExtensions` 会自动安装。

### Cursor AI

*   `settings.json`: Cursor 的用户设置。
*   `extensions.txt`: Cursor 扩展清单。

## GitHub Actions

仓库中包含了 `.github/workflows/main.yml` 文件，它定义了一个 GitHub Actions 工作流。这个工作流目前只能手动触发（`workflow_dispatch`），以验证 `install.sh` 脚本是否能成功执行，并检查关键配置文件的内容是否符合预期。这有助于确保你的 dotfiles 始终保持可用和正确。

## 自定义

你可以根据自己的需求修改仓库中的任何配置文件。修改后，重新运行 `install.sh` 脚本即可更新你的系统配置。

## 贡献

欢迎通过 Pull Request 提交改进或建议。

## 许可证

本项目采用 MIT 许可证。

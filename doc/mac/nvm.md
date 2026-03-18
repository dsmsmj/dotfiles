# macOS：使用 nvm 管理 Node.js 版本

macOS 上推荐使用 **nvm** 管理多个 Node.js 版本，避免不同项目对 Node 版本要求不一致。

## 前置条件

- 建议安装 Homebrew：`https://brew.sh/`
- 使用 zsh（macOS 默认）：配置文件通常是 `~/.zshrc`（bash 则是 `~/.bashrc` / `~/.bash_profile`）

## 安装 nvm（推荐：Homebrew）

```bash
brew install nvm
```

创建 nvm 工作目录：

```bash
mkdir -p ~/.nvm
```

把以下内容追加到 `~/.zshrc`（bash 用户改到对应 rc 文件）：

```bash
export NVM_DIR="$HOME/.nvm"
  [ -s "/opt/homebrew/opt/nvm/nvm.sh" ] && . "/opt/homebrew/opt/nvm/nvm.sh"
  [ -s "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm" ] && . "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm"
```

> Intel Mac 的 Homebrew 前缀可能是 `/usr/local`，如果你不是 Apple Silicon，把上面路径的 `/opt/homebrew` 替换为 `/usr/local`。

重新加载配置：

```bash
source ~/.zshrc
```

验证：

```bash
nvm --version
```

## 常用命令

### 查看可安装版本（远端）

```bash
nvm ls-remote
```

### 安装指定版本

```bash
nvm install 20.11.1
```

### 查看已安装版本

```bash
nvm ls
```

### 切换版本

```bash
nvm use 20.11.1
node -v
```

### 设置默认版本（新 shell 自动使用）

```bash
nvm alias default 20.11.1
```

## 常见问题（macOS）

### 1) 重开终端后 `nvm` 又找不到

说明你的 shell 启动文件没有正确加载 nvm。优先检查：

- 你用的是 zsh 还是 bash（`echo $SHELL`）
- `~/.zshrc` / `~/.bashrc` 里是否有 `NVM_DIR` 与 `nvm.sh` 的加载

### 2) 项目需要自动切 Node 版本（.nvmrc）

在项目根目录放一个 `.nvmrc`（内容是版本号，例如 `20.11.1`），进入目录后：

```bash
nvm use
```


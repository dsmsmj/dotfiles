# macOS：安装与使用 Bun

Bun 是一个集成的 JavaScript runtime / bundler / 包管理器，常见用法包括：`bun install`、`bun run`、`bunx`。

## 安装

### 方式 A：官方安装脚本（推荐）

```bash
curl -fsSL https://bun.sh/install | bash
```

安装后按提示把 Bun 的 PATH 初始化加入 shell（通常会提示加入到 `~/.zshrc`）。

重新加载配置并验证：

```bash
source ~/.zshrc
bun --version
which bun
```

### 方式 B：Homebrew

```bash
brew install oven-sh/bun/bun
```

验证：

```bash
bun --version
which bun
```

## 常用命令

```bash
bun init
bun install
bun run dev
bunx <pkg> [args...]
```

## 常见问题（macOS）

### 1) Node / npm / pnpm / yarn 能不能和 bun 共存？

可以。建议团队统一一种包管理/lockfile，避免混用：

- Bun：`bun.lockb`
- npm：`package-lock.json`
- pnpm：`pnpm-lock.yaml`
- yarn：`yarn.lock`


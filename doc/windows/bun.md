# Windows：安装与使用 Bun

Bun 是一个集成的 JavaScript runtime / bundler / 包管理器，常见用法包括：`bun install`、`bun run`、`bunx`。

## 安装（推荐）

### 方式 A：官方安装脚本（PowerShell）

```powershell
powershell -c "irm bun.sh/install.ps1 | iex"
```

安装后新开终端验证：

```powershell
bun --version
where bun
```

> 如果 `where bun` 找不到，通常是终端未刷新 PATH：关闭所有终端/重启 Cursor 后再试。

### 方式 B：Scoop（如果你已在用）

```powershell
scoop install bun
```

## 常用命令

### 初始化项目

```powershell
bun init
```

### 安装依赖

```powershell
bun install
```

### 运行 package.json 脚本

```powershell
bun run dev
```

### 临时执行包（类似 npx）

```powershell
bunx <pkg> [args...]
```

## 常见问题（Windows）

### 1) Node / npm / pnpm / yarn 能不能和 bun 共存？

可以。Bun 自带包管理器，但你仍然可以按项目需要使用 npm/pnpm/yarn。建议团队统一一种方案，避免 lockfile 混用：

- Bun：`bun.lockb`
- npm：`package-lock.json`
- pnpm：`pnpm-lock.yaml`
- yarn：`yarn.lock`

### 2) 公司网络/代理导致安装失败

优先使用公司允许的代理方式或包管理器（例如 Scoop）。如果你在用 `npmrc` 里配置了镜像/代理，Bun 仍可能需要单独配置网络环境。


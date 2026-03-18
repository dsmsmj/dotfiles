# Windows：安装与使用 pnpm（推荐用 Corepack）

pnpm 是高性能包管理器，很多全栈仓库（尤其是 monorepo）默认使用 pnpm。推荐用 **Corepack** 管理 pnpm 版本，确保可复现。

## 前置条件

- 已安装 Node.js（建议用 `doc/windows/nvm.md` 管理版本）
- Node.js 版本建议 \(>= 16.10\)

## 安装/启用 pnpm（Corepack）

### 1) 启用 Corepack

```powershell
corepack enable
```

### 2) 准备并激活 pnpm

```powershell
corepack prepare pnpm@latest --activate
```

验证：

```powershell
pnpm -v
where pnpm
```

## 项目内固定 pnpm 版本（推荐）

如果项目的 `package.json` 里声明了 `packageManager`（例如 `pnpm@9.x`），Corepack 会自动用对应版本。

你也可以在项目根目录运行（会写入 `packageManager` 字段）：

```powershell
corepack use pnpm@latest
```

## 常用命令

```powershell
pnpm install
pnpm add <pkg>
pnpm add -D <pkg>
pnpm remove <pkg>
pnpm run <script>
pnpm dlx <pkg> [args...]
pnpm -r run build
```

## 常见问题（Windows）

### 1) `pnpm` 命令找不到

按顺序排查：

```powershell
node -v
corepack -v
corepack enable
corepack prepare pnpm@latest --activate
pnpm -v
```

### 2) 切 Node 版本后 pnpm 不见了

如果你用 nvm 切换 Node 版本，建议在每个版本下都执行一次：

```powershell
corepack enable
```

然后再 `corepack prepare ... --activate`。

### 3) store 占用 C 盘空间

pnpm 的 store 默认在用户目录附近。你可以用：

```powershell
pnpm store path
```

如果需要迁移 store（例如到 D 盘），建议在团队约定前先统一策略，避免不同机器路径差异导致困惑。


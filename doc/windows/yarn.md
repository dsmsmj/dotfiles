# Windows：安装与使用 Yarn（推荐用 Corepack）

从 Yarn 2+ 开始，官方推荐用 **Corepack**（随 Node.js 一起发布）来管理 Yarn 版本，这样更可控、也更容易复现。

## 前置条件

- 已安装 Node.js（建议用本仓库的 nvm-windows 流程管理版本）：`doc/windows/nvm.md`
- Node.js 版本建议 \(>= 16.10\)（Corepack 起步版本更早，但新版本更稳）

## 安装/启用 Yarn（Corepack）

### 1) 启用 Corepack

```powershell
corepack enable
```

### 2) 准备并激活 Yarn

推荐让 Corepack 负责下载并激活一个 Yarn 版本：

```powershell
corepack prepare yarn@stable --activate
```

验证：

```powershell
yarn -v
where yarn
```

## 项目内固定 Yarn 版本（推荐）

让项目自行声明 Yarn 版本（写入 `package.json` 的 `packageManager` 字段）：

```powershell
yarn set version stable
```

之后团队成员只要启用了 Corepack，进入项目目录执行 `yarn` 就会自动使用项目声明的版本。

## 常用命令

```powershell
yarn install
yarn add <pkg>
yarn add -D <pkg>
yarn remove <pkg>
yarn run <script>
yarn dlx <pkg> [args...]
```

## 常见问题（Windows）

### 1) `yarn` 命令找不到

按顺序排查：

```powershell
node -v
corepack -v
corepack enable
corepack prepare yarn@stable --activate
yarn -v
```

### 2) 全局 yarn（npm i -g yarn）和 Corepack 冲突

不建议用 `npm i -g yarn`。如果你以前装过全局 yarn，可能导致 `where yarn` 指向旧位置。

建议卸载全局 yarn（如果确定不再需要）：

```powershell
npm uninstall -g yarn
```

然后回到 Corepack 流程。


# macOS：安装与使用 Yarn（推荐用 Corepack）

从 Yarn 2+ 开始，官方推荐用 **Corepack**（随 Node.js 一起发布）来管理 Yarn 版本，这样更可控、也更容易复现。

## 前置条件

- 已安装 Node.js（建议用 `doc/mac/nvm.md` 的 nvm 管理版本）
- Node.js 版本建议 \(>= 16.10\)

## 安装/启用 Yarn（Corepack）

### 1) 启用 Corepack

```bash
corepack enable
```

### 2) 准备并激活 Yarn

```bash
corepack prepare yarn@stable --activate
```

验证：

```bash
yarn -v
which yarn
```

## 项目内固定 Yarn 版本（推荐）

让项目自行声明 Yarn 版本（写入 `package.json` 的 `packageManager` 字段）：

```bash
yarn set version stable
```

之后团队成员只要启用了 Corepack，进入项目目录执行 `yarn` 就会自动使用项目声明的版本。

## 常用命令

```bash
yarn install
yarn add <pkg>
yarn add -D <pkg>
yarn remove <pkg>
yarn run <script>
yarn dlx <pkg> [args...]
```

## 常见问题（macOS）

### 1) `yarn` 命令找不到

按顺序排查：

```bash
node -v
corepack -v
corepack enable
corepack prepare yarn@stable --activate
yarn -v
```

### 2) 全局 yarn（npm i -g yarn）和 Corepack 冲突

不建议用 `npm i -g yarn`。如果你以前装过全局 yarn，可能导致 `which yarn` 指向旧位置。

建议卸载全局 yarn（如果确定不再需要）：

```bash
npm uninstall -g yarn
```


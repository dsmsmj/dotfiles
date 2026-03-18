# 环境搭建手册（总导航）

这里是本仓库的“新机器环境搭建”文档索引。建议按“装机顺序”走一遍，避免遗漏或顺序不当导致踩坑。

## 装机顺序（建议）

### 1) 基础工具

- Git（系统自带或安装最新版）
- 终端（Windows Terminal / iTerm2 等，按你的系统选择）

### 2) 代码拉取与 SSH

- Git + SSH（生成 key、添加到 GitHub/GitLab、常见报错排查）
  - Windows：`windows/git-ssh.md`
  - macOS：`mac/git-ssh.md`

### 3) Node.js 运行时与包管理

- Node.js 版本管理
  - Windows：`windows/nvm.md`
  - macOS：`mac/nvm.md`
- Yarn（建议 Corepack）
  - Windows：`windows/yarn.md`
  - macOS：`mac/yarn.md`
- pnpm（建议 Corepack）
  - Windows：`windows/pnpm.md`
  - macOS：`mac/pnpm.md`
- Bun（可选）
  - Windows：`windows/bun.md`
  - macOS：`mac/bun.md`

### 4) 容器与本地依赖

- Docker
  - Windows：`windows/docker.md`
  - macOS：`mac/docker.md`
- 本地数据库（docker compose 一键起）
  - `shared/databases.md`
  - `shared/compose/databases.compose.yml`

### 5) 后端构建工具（按你技术栈）

- Maven
  - Windows：`windows/maven.md`
  - macOS：`mac/maven.md`

## 文档索引

### Windows

- `windows/git-ssh.md`
- `windows/nvm.md`
- `windows/yarn.md`
- `windows/pnpm.md`
- `windows/bun.md`
- `windows/docker.md`
- `windows/maven.md`

### macOS

- `mac/git-ssh.md`
- `mac/nvm.md`
- `mac/yarn.md`
- `mac/pnpm.md`
- `mac/bun.md`
- `mac/docker.md`
- `mac/maven.md`
- `mac/cursor-user-snippets-symlink.md`

### Shared（跨平台）

- `shared/databases.md`
- `shared/compose/databases.compose.yml`


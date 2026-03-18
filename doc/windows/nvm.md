# Windows：使用 nvm 管理 Node.js 版本（nvm-windows）

本仓库在 Windows 上推荐使用 **nvm-windows** 来管理多个 Node.js 版本，避免手动安装/卸载造成的 PATH 冲突。

## 安装

### 方式 A：安装包（推荐）

1. 打开 nvm-windows Releases：`https://github.com/coreybutler/nvm-windows/releases`
2. 下载最新版 `nvm-setup.exe`
3. 双击安装，保持默认选项即可
4. 安装完成后 **新开一个 PowerShell**，验证：

```powershell
nvm version
```

如果提示找不到 `nvm`，通常是终端未刷新环境变量：关闭所有终端/重启 Cursor 后再试。

### 方式 B：Chocolatey（如果你已在用）

```powershell
choco install nvm -y
```

安装后同样新开终端验证：

```powershell
nvm version
```

## 常用命令

### 查看远端可安装版本

```powershell
nvm list available
```

### 安装指定版本

```powershell
nvm install 20.11.1
```

### 查看本机已安装版本

```powershell
nvm list
```

### 切换版本（全局生效）

```powershell
nvm use 20.11.1
```

### 查看当前 node / npm 版本

```powershell
node -v
npm -v
```

## 推荐工作流示例

同时安装一个旧 LTS 和一个新版本，按项目需要随时切换：

```powershell
nvm install 18.20.5
nvm install 20.11.1

nvm use 20.11.1
node -v
```

## 常见问题（Windows）

### 1) 之前装过官方 Node 安装包，切换后版本不对

可能是旧版 Node 的路径仍在 PATH 中或残留安装。

建议：
- 先在“设置 → 应用”里卸载旧的 Node.js（如果你确定要全面改用 nvm）
- 重新打开终端后再执行 `nvm use <version>`
- 用下面命令确认当前命令来自哪里：

```powershell
where node
where npm
```

### 2) 切换版本后，全局 npm 包没了

这是正常现象：不同 Node 版本的全局包目录通常不同。切到某个版本后，需要在该版本下重新安装全局工具，例如：

```powershell
npm i -g pnpm
```


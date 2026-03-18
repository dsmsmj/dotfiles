# Windows：安装与使用 Docker（Docker Desktop + WSL2）

Windows 上最常见的 Docker 方案是 **Docker Desktop + WSL2 backend**。本文记录安装路径、必要开关、以及最常见的坑。

## 安装 Docker Desktop

1. 下载 Docker Desktop（官方）：`https://www.docker.com/products/docker-desktop/`
2. 安装时建议勾选/启用 WSL2 相关选项（如果安装器有提示）
3. 安装后打开 Docker Desktop，完成首次初始化

验证（PowerShell）：

```powershell
docker version
docker info
```

## 启用/确认 WSL2（推荐）

在管理员 PowerShell 执行（若已启用可跳过）：

```powershell
wsl --install
```

确认 WSL 状态与版本：

```powershell
wsl --status
wsl -l -v
```

推荐把默认版本设为 2：

```powershell
wsl --set-default-version 2
```

## Docker Desktop 常用设置建议

- **General**：Use the WSL 2 based engine（开启）
- **Resources → WSL Integration**：为你的发行版开启集成（比如 Ubuntu）
- **Resources**：按机器配置调整 CPU/Memory（容器跑不动时优先看这里）

## 常用命令

```powershell
docker ps
docker images
docker pull <image>
docker run --rm -it <image> <cmd>
docker compose version
docker compose up -d
docker compose logs -f
```

## 常见问题（Windows）

### 1) `docker` 命令存在，但启动/拉取镜像很慢或失败

常见原因：
- 公司网络需要代理
- DNS 被污染/解析慢

建议：
- 在 Docker Desktop 的 Settings 里配置 HTTP/HTTPS Proxy（如果公司要求）
- 或在 WSL 发行版内配置代理/DNS（看你主要在 Windows 还是 WSL 里跑 docker）

### 2) 端口被占用（例如 3000/5432/6379）

用下面命令查占用：

```powershell
netstat -ano | findstr :3000
```

然后根据 PID 关闭占用进程，或在 `docker-compose.yml` 改宿主机端口映射。

### 3) 路径与性能：把项目放在哪更好？

如果你主要在 **WSL2** 里开发（推荐），把代码放在 WSL 的 Linux 文件系统里（例如 `\\wsl$\\Ubuntu\\home\\<you>\\project` 对应的路径），通常 I/O 性能更好。

如果你主要在 **Windows** 里开发（VSCode/Cursor 直接打开 Windows 路径），也能用 Docker Desktop，但大项目可能会遇到 I/O 慢的问题。

### 4) 和 Hyper-V 的关系

Docker Desktop 现在主流是 WSL2 backend；如果你机器/公司策略限制 WSL2，才会考虑 Hyper-V/旧方案。优先按 WSL2 路线走。


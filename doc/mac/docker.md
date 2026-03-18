# macOS：安装与使用 Docker

macOS 上最常见的 Docker 方案是 **Docker Desktop**。如果你更想要轻量/开源方案，也可以用 **Colima**（基于 Lima）。

## 方案 A：Docker Desktop（最省心）

1. 下载并安装 Docker Desktop：`https://www.docker.com/products/docker-desktop/`
2. 打开 Docker Desktop，完成首次初始化

验证：

```bash
docker version
docker info
docker compose version
```

## 方案 B：Colima（轻量、偏开发者）

### 安装

```bash
brew install colima docker docker-compose
```

启动：

```bash
colima start
```

验证：

```bash
docker version
docker info
```

停止：

```bash
colima stop
```

## 常用命令

```bash
docker ps
docker images
docker pull <image>
docker run --rm -it <image> <cmd>
docker compose up -d
docker compose logs -f
```

## 常见问题（macOS）

### 1) Docker Desktop 启动失败或资源占用高

优先检查 Docker Desktop 的 Settings（CPU/Memory/Disk），并确认是否有大量容器/镜像占用磁盘。

### 2) 公司网络/代理导致拉取镜像失败

在 Docker Desktop Settings 中配置代理（如果公司要求）。若使用 Colima，则需要按你的 shell/系统代理方式配置网络环境。


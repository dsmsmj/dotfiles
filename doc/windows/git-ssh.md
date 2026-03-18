# Windows：Git SSH（生成 Key / 配置 GitHub / 常见问题）

本文用于在 Windows 上配置 Git 通过 SSH 访问远端（GitHub/GitLab），避免每次输入账号密码。

## 1) 生成 SSH Key

推荐用 ed25519：

```powershell
ssh-keygen -t ed25519 -C "your_email@example.com"
```

一路回车即可（默认会生成到 `C:\Users\<you>\.ssh\`）。

查看公钥：

```powershell
type $env:USERPROFILE\.ssh\id_ed25519.pub
```

把输出内容复制到 GitHub/GitLab 的 SSH Keys。

## 2) 启动 ssh-agent 并加载 key（可选但推荐）

```powershell
Get-Service ssh-agent | Set-Service -StartupType Automatic
Start-Service ssh-agent
ssh-add $env:USERPROFILE\.ssh\id_ed25519
```

验证：

```powershell
ssh-add -l
```

## 3) 测试连接

GitHub：

```powershell
ssh -T git@github.com
```

首次连接会提示是否信任主机指纹，输入 `yes`。

## 4) 常用的 ~/.ssh/config（多账号/指定 key）

编辑 `~/.ssh/config`（本仓库也有 `ssh/config` 可管理）示例：

```sshconfig
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
```

如果你有多个 GitHub 账号，可以用别名：

```sshconfig
Host github-work
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_work
  IdentitiesOnly yes
```

此时仓库 remote 用：

```powershell
git remote set-url origin git@github-work:ORG/REPO.git
```

## 常见问题

### 1) `Permission denied (publickey)`

排查思路：

```powershell
where ssh
ssh -vT git@github.com
```

重点看：
- 是否加载了正确的 key（`ssh-add -l`）
- `~/.ssh/config` 是否指定了正确的 `IdentityFile`

### 2) `Host key verification failed`

说明 `known_hosts` 里的记录不匹配（换了网络/中间人代理/记录损坏）。

可以删除对应条目后重试（谨慎操作）：

```powershell
ssh-keygen -R github.com
ssh -T git@github.com
```


# macOS：Git SSH（生成 Key / 配置 GitHub / 常见问题）

本文用于在 macOS 上配置 Git 通过 SSH 访问远端（GitHub/GitLab），避免每次输入账号密码。

## 1) 生成 SSH Key

推荐用 ed25519：

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

查看公钥：

```bash
cat ~/.ssh/id_ed25519.pub
```

把输出内容复制到 GitHub/GitLab 的 SSH Keys。

## 2) 加载 key（ssh-agent）

macOS 通常会自动管理 ssh-agent，但建议显式加入：

```bash
eval "$(ssh-agent -s)"
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
```

验证：

```bash
ssh-add -l
```

## 3) 测试连接

GitHub：

```bash
ssh -T git@github.com
```

首次连接会提示是否信任主机指纹，输入 `yes`。

## 4) 常用的 ~/.ssh/config（多账号/指定 key）

示例：

```sshconfig
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
  AddKeysToAgent yes
  UseKeychain yes
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

```bash
git remote set-url origin git@github-work:ORG/REPO.git
```

## 常见问题

### 1) `Permission denied (publickey)`

用 verbose 看细节：

```bash
ssh -vT git@github.com
```

重点看：
- 是否选中了正确的 key
- `~/.ssh/config` 是否指定了正确的 `IdentityFile`

### 2) `Host key verification failed`

可以删除对应条目后重试（谨慎操作）：

```bash
ssh-keygen -R github.com
ssh -T git@github.com
```


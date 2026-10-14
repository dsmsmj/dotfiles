# WSL（Ubuntu）里在系统默认 ~/.bashrc 之外的自定义部分。
# install.sh 会在 ~/.bashrc 末尾加一行 source 引入本文件，不覆盖默认 .bashrc。

# 代理：Windows 上的 Clash 等代理端口。配合 .wslconfig 里的 networkingMode=mirrored，
# WSL 里的 127.0.0.1 就是 Windows 本机。
export http_proxy="http://127.0.0.1:7897"
export https_proxy="http://127.0.0.1:7897"
export ALL_PROXY="socks5://127.0.0.1:7897"

export PATH="$HOME/.local/bin:$PATH"

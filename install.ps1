# Windows 版安装脚本：把仓库里的配置链接到对应位置。
# 用法（管理员 PowerShell，或已开启“开发者模式”以允许创建符号链接）：
#   git clone https://github.com/dsmsmj/dotfiles.git $HOME\dotfiles
#   powershell -ExecutionPolicy Bypass -File $HOME\dotfiles\install.ps1
# 加 -InstallExtensions 同时安装 VS Code / Cursor 扩展。
param([switch]$InstallExtensions)
$ErrorActionPreference = 'Stop'
$Dot = $PSScriptRoot

function Link-File($Source, $Target) {
    $dir = Split-Path $Target
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    if (Test-Path $Target) {
        $item = Get-Item $Target -Force
        if ($item.LinkType -eq 'SymbolicLink' -and $item.Target -eq $Source) { Write-Host "已链接: $Target"; return }
        Write-Host "备份: $Target -> $Target.bak"
        Move-Item $Target "$Target.bak" -Force
    }
    New-Item -ItemType SymbolicLink -Path $Target -Target $Source | Out-Null
    Write-Host "链接: $Target -> $Source"
}

Link-File "$Dot\git\.gitconfig"      "$HOME\.gitconfig"
Link-File "$Dot\node\.npmrc"         "$HOME\.npmrc"
Link-File "$Dot\ssh\config"          "$HOME\.ssh\config"
Link-File "$Dot\wsl\.wslconfig"      "$HOME\.wslconfig"

$code   = "$env:APPDATA\Code\User"
$cursor = "$env:APPDATA\Cursor\User"
Link-File "$Dot\vscode\settings.json"    "$code\settings.json"
Link-File "$Dot\vscode\keybindings.json" "$code\keybindings.json"
Link-File "$Dot\vscode\snippets"         "$code\snippets"
Link-File "$Dot\cursor\settings.json"    "$cursor\settings.json"
Link-File "$Dot\vscode\snippets"         "$cursor\snippets"

# Windows Terminal
$wt = Get-ChildItem "$env:LOCALAPPDATA\Packages" -Directory -Filter 'Microsoft.WindowsTerminal_*' -ErrorAction SilentlyContinue | Select-Object -First 1
if ($wt) { Link-File "$Dot\windows-terminal\settings.json" "$($wt.FullName)\LocalState\settings.json" }

# Cursor 用户级：rules / developer-context 链接，skills 和 mcp 只在缺失时复制
Link-File "$Dot\.cursor\rules"             "$HOME\.cursor\rules"
Link-File "$Dot\.cursor\developer-context" "$HOME\.cursor\developer-context"
function Copy-IfMissing($Source, $Target) {
    if (-not (Test-Path $Target)) {
        New-Item -ItemType Directory -Path (Split-Path $Target) -Force | Out-Null
        Copy-Item $Source $Target -Recurse
        Write-Host "复制: $Target"
    }
}
foreach ($s in 'diff-git-review','quick-git-commit-no-verify','legacy-feature-kickoff','mvp-functional-refactor','product-docs-query') {
    Copy-IfMissing "$Dot\.cursor\skills\$s" "$HOME\.cursor\skills\$s"
}
Copy-IfMissing "$Dot\cuddy\dev-team-dialogue" "$HOME\.cursor\skills\dev-team-dialogue"
Copy-IfMissing "$Dot\.cursor\mcp.json" "$HOME\.cursor\mcp.json"

# Codex：config 只在缺失时复制（Codex 会持续改写它），rules/skills 同理
Copy-IfMissing "$Dot\codex\config.toml"   "$HOME\.codex\config.toml"
Copy-IfMissing "$Dot\codex\rules"         "$HOME\.codex\rules"
foreach ($s in 'image-designer','skill-smoke-test') { Copy-IfMissing "$Dot\codex\skills\$s" "$HOME\.codex\skills\$s" }
foreach ($s in 'diff-git-review','quick-git-commit-no-verify') { Copy-IfMissing "$Dot\.cursor\skills\$s" "$HOME\.codex\skills\$s" }

if (-not (Test-Path "$HOME\.gitconfig.local")) {
    Copy-Item "$Dot\git\.gitconfig.local.example" "$HOME\.gitconfig.local"
    Write-Host "已生成 ~/.gitconfig.local，按需填写本机身份"
}
if (-not (Test-Path "$HOME\.m2\settings.xml")) {
    New-Item -ItemType Directory -Path "$HOME\.m2" -Force | Out-Null
    Copy-Item "$Dot\maven\settings.template.xml" "$HOME\.m2\settings.xml"
    Write-Host "已生成 ~/.m2/settings.xml，记得填私服地址和账号"
}

if ($InstallExtensions) {
    foreach ($pair in @(@('code', "$Dot\vscode\extensions.txt"), @('cursor', "$Dot\cursor\extensions.txt"))) {
        $cli, $list = $pair
        if (Get-Command $cli -ErrorAction SilentlyContinue) {
            Get-Content $list | Where-Object { $_ -and -not $_.StartsWith('#') } | ForEach-Object { & $cli --install-extension $_ }
        } else { Write-Host "未找到 $cli 命令，跳过扩展安装" }
    }
}
Write-Host "dotfiles 安装完成"

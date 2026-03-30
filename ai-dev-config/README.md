# Personal AI Dev Config

个人开发配置，一个"真相源"，Cursor / Claude Code / Copilot 同时读。

## 结构

```
[本仓库 dotfiles]/
├── .cursor/
│   ├── developer-context/   ← 真相源（identity / stack / patterns，内容在这里改）
│   └── rules/               ← Cursor 规则（可 symlink 到 ~/.cursor/rules）
│       ├── 00-self.mdc      全局基调（alwaysApply: true）
│       ├── 01-code.mdc      …
│       └── …
│
ai-dev-config/                 ← 与 .cursor 同步的模板副本（cursor-rules、claude）
├── cursor-rules/
└── claude/CLAUDE.md

~/
├── .claude/CLAUDE.md        ← symlink 到本仓库 ai-dev-config/claude/CLAUDE.md
└── [project]/.cursor/rules/project.mdc   ← 仅项目差异
```

## 部署

克隆本仓库后，在每台机器上自行链到（或复制到）对应目录即可：

- 可选：`.cursor/developer-context/` → `~/.config/developer-context/`（或沿用既有 `~/.config/ai-dev/`）
- `ai-dev-config/cursor-rules/*.mdc` 或直接用 `.cursor/rules/*.mdc` → `~/.cursor/rules/`
- `ai-dev-config/claude/CLAUDE.md` → `~/.claude/CLAUDE.md`

macOS/Linux 用 `ln -s`；Windows 可用 junction/复制，视权限而定。

## 日常使用

| 我说        | 触发规则             | 效果                     |
|-----------|------------------|------------------------|
| /review   | 05-review.mdc    | P0/P1/P2 分级 review     |
| /component UserCard 用户头像卡片 | skill-component  | 生成符合规范的组件 |
| /api user create | skill-api-route  | 生成完整分层的 API         |
| /refactor | skill-refactor   | 安全重构，先问后动           |
| /debug 按钮点击无响应 | skill-debug  | 假设列表 + 验证方法         |

## 维护原则

跟 AI 扯皮超过 2 个来回 → 事后把结论写进对应文件：
- 沟通方式问题 → identity.md
- 技术选型问题 → stack.md
- 解法模式问题 → patterns.md
- 特定任务流程 → 对应 skill-*.mdc

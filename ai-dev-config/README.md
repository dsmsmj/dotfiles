# Personal AI Dev Config

个人开发配置，一个"真相源"，Cursor / Claude Code / Copilot 同时读。

## 结构

```
~/
├── .config/ai-dev/          ← 真相源（内容在这里改）
│   ├── identity.md          你是谁：沟通方式、价值观、硬约束
│   ├── stack.md             你用什么：技术选型、约定
│   └── patterns.md          你怎么做：已验证的解法模式
│
├── .cursor/rules/           ← Cursor 全局规则（symlink 到这个 repo）
│   ├── 00-self.mdc          全局基调（alwaysApply: true）
│   ├── 01-code.mdc          代码硬约束（alwaysApply: true）
│   ├── 02-react.mdc         React/Next（按 .tsx 触发）
│   ├── 03-node.mdc          Node/API（按路径触发）
│   ├── 04-python.mdc        Python（按 .py 触发）
│   ├── 05-review.mdc        /review 触发
│   ├── skill-component.mdc  /component 触发
│   ├── skill-api-route.mdc  /api 触发
│   ├── skill-refactor.mdc   /refactor 触发
│   └── skill-debug.mdc      /debug 触发
│
├── .claude/
│   └── CLAUDE.md            ← Claude Code 全局配置（symlink）
│
└── [project]/
    └── .cursor/rules/
        └── project.mdc      ← 只写这个项目和全局的差异
```

## 部署

克隆本仓库后，在每台机器上自行把文件链到（或复制到）对应目录即可：

- `ai-dev/*.md` → `~/.config/ai-dev/`
- `cursor-rules/*.mdc` → `~/.cursor/rules/`
- `claude/CLAUDE.md` → `~/.claude/CLAUDE.md`

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

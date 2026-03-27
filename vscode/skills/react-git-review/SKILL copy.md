---
name: react-git-review
description: >-
  Reviews staged git changes (git diff --cached) for React/TypeScript/JSX projects
  using a layered checklist (hooks, effects, performance, a11y, types). Use when
  the user wants to review staged changes, asks for a pre-commit code review,
  pairs "git add" with review, or says phrases like "帮我 review 暂存的更改",
  "review 一下我的改动", "提交前帮我看看", "check my staged changes", or
  "review before commit". Apply for any React/TS/JSX diff review, including
  partial or quick checks.
---

# React Git Review 协议

## 0. 启动指令 (优先级顺序)
1. **自动获取**：若用户未提供 diff，立即执行：
   `git diff --cached && git diff --cached --stat && git log --oneline -5`
2. **环境识别**：检索 `package.json` 确认 React, Next, Vite, Tailwind, TanStack Query, Webpack 等核心栈。

## 1. 审查准则 (无废话检查点)

### 🔴 必须修复 (Blocking)
- **React**: Hook 调用位置、`useEffect` 闭包陷阱/死循环、State 直接修改、列表 `key={index}`。
- **TS**: `any` 滥用、非空断言 `!` 风险、Props 类型缺失。
- **性能**: 渲染内匿名函数引发的子组件重绘、大数据量无 Virtualization、昂贵计算未 `useMemo`。

### 🟡 建议修改 (Optimization)
- **设计**: 组件 > 150 行未拆分、Props Drilling > 3 层、异步缺少 Loading/Error 状态。
- **逻辑**: 可派生状态误用 `useState`、多个关联 State 未合并。

### 🟢 可选优化 (Style)
- **规范**: 魔法值未常量化、重复逻辑未抽离 Hook、命名冲突。

## 2. 输出协议 (严格格式)

### 🚨 发现问题
## Code Review — [文件名/功能]
### 🔴 必须修复 ([N]项)
- **[标题]** | `文件:行号`
- **问题**: [简述原因]
- **修改**: 
```tsx
// Before -> After 对比块
```

### 无问题时

- `## Code Review — [描述]`
- 正文：`代码质量良好，可以提交。`
- `亮点：` 可选，一两句即可

输出中可使用 🔴🟡🟢 与「必须修复 / 建议修改 / 可选优化」对应，与上文维度一致。

审查通过后，询问用户：
「代码质量良好。是否需要生成 commit message 和 PR 描述？」

若用户确认，按 06-git 规范输出：
1. Commit message（遵循 `type(scope): 描述` 格式）
2. PR 描述（改了什么 + 关键文件 + 破坏性变更标注）

**执行要求**：
- 对于 Commit，请**提供可直接复制并在 CMD/PowerShell 中执行的完整指令**，例如：
  ```bash
  git commit -m "..." -m "..."
  ```
---
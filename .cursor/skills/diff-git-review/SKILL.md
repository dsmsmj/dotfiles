---
name: diff-git-review
description: >-
  Reviews staged git changes (git diff --cached) for React/TypeScript/JSX projects
  using a layered checklist (hooks, effects, performance, a11y, types). Use when
  the user wants to review staged changes, asks for a pre-commit code review,
  pairs "git add" with review, or says phrases like "帮我 review 暂存的更改",
  "review 一下我的改动", "提交前帮我看看", "check my staged changes", or
  "review before commit". Apply for any React/TS/JSX diff review, including
  partial or quick checks.
---

# diff Git Review 协议

## 0. 启动指令与环境感知
1. **主动获取上下文**：如果用户要求 Review 但未明确提供 diff 内容，请主动**利用工具执行终端命令**（须使用执行命令的工具）：
   - `git diff --cached` (获取暂存区的代码改动)
   - `git diff --cached --stat` (获取改动的文件概览)
   - `git log --oneline -5` (了解近期的提交记录，以便生成更准确的 commit message)
2. **环境识别**：根据工作区中的 `package.json` 等文件，识别当前项目是否使用了特定框架（如 Next.js, Vite, Tailwind CSS 等），以便提供框架相关的针对性建议。

## 1. 审查准则 (无废话检查点)

请根据以下优先级层次对 diff 进行严格审查：

### 🔴 必须修复 (Blocking)
- **React**: Hook 调用位置是否合法（避免条件调用）、`useEffect` 是否存在闭包陷阱或造成死循环的隐患、State 是否被直接变异（Mutate）修改、列表渲染的 `key` 是否使用了不稳定的 `index`。
- **TypeScript**: 是否滥用 `any` 绕过类型检查、是否存在危险的非空断言 `!`、Props 类型声明是否完整。
- **性能**: 渲染函数内是否存在会导致子组件不必要重绘的匿名函数/对象、大数据量渲染是否缺失虚拟化（Virtualization）、昂贵的计算逻辑是否未使用 `useMemo`。
- **安全**: **绝对禁止**提交敏感信息（如 API Key、Token、私钥等），一旦发现立即阻断。

### 🟡 建议修改 (Optimization)
- **代码结构**: 单个组件是否超过 150 行且未拆分、Props Drilling（属性钻取）是否超过 3 层、异步操作（如网络请求）是否缺失完整的 Loading 和 Error 状态处理。
- **状态管理**: 可以通过现有 State 派生出的数据是否误用了多余的 `useState`、多个强关联的 State 是否未合并或未使用 `useReducer`。

### 🟢 可选优化 (Style & Maintenance)
- **规范**: 魔法字符串/魔法数字是否未提取为常量、重复逻辑是否可以抽离为 Custom Hook、命名是否会引起歧义。
- **可访问性 (a11y)**: `<img>` 等标签是否缺失语义化的属性（如 `alt`）。

## 2. 输出协议 (严格统一结构)

请严格按照以下模板输出你的 Review 结果（若某一级别无问题，则直接省略该分类）：

````markdown
### 🔍 Git Diff Review 结果

**🔴 必须修复 (Blocking)**
- `[文件名:行号]` 简述问题 —— **修复建议**: 提供具体的修复思路或代码片段

**🟡 建议修改 (Optimization)**
- `[文件名:行号]` 简述问题 —— **优化建议**: 提供具体的优化思路或代码片段

**🟢 可选优化 (Style)**
- `[文件名:行号]` 简述问题 —— **改进建议**: 提供具体的改动思路
````

## 3. 自动衔接逻辑 (无感闭环)
- **若存在“🔴 必须修复”项**：输出完 Review 结果后必须停止，严格提示用户：“**当前存在 Blocking 级别的缺陷，请务必修复后再考虑提交。**”（此时**不允许**提供快捷提交建议）。
- **若代码质量良好（仅存在轻微建议或无问题）**：在输出末尾，无需询问用户，直接依据 Conventional Commits 规范自动生成一键提交命令：

  ---
  ### 🚀 快捷提交建议 (Git Commit)
  *依据本次改动自动生成，如满意可直接复制执行：*

  ```bash
  git commit -m "feat/fix/refactor(scope): 简述改动" -m "- 详细说明改动点 1" -m "- 详细说明改动点 2"
  ```
  *(💡 提示：如果确认无需进行 lint/代码格式化等 pre-commit 检查，可在末尾添加 `-n` 参数跳过检查)*
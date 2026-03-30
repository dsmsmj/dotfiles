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

# React Git Review

专为 React 项目设计的**暂存区**代码审查流程。只审查 `git diff --cached` 范围内的改动；若用户已粘贴 diff，可直接基于粘贴内容审查。

## 工作流程

**Step 1：获取暂存区变更**

若用户未提供 diff，在仓库根目录执行：

```bash
git diff --cached
git diff --cached --stat
git log --oneline -5
```

**Step 2：识别项目上下文**

读取根目录 `package.json`，识别技术栈：`react`、`typescript`、`next`、`vite`、`redux`、`zustand`、`@tanstack/react-query`、`tailwind` 等。

**Step 3：按下方维度分层审查**

---

## 审查维度

### 🔴 必须修复

**React 核心**
- Hook 规则：条件/循环内调用；组件外误用
- `useEffect` 依赖数组完全缺失（stale closure）或错误（无限循环）
- `useEffect` 内异步回调未处理竞态（缺少 cleanup / ignore flag）
- 异步回调完成时组件已卸载仍调用 setter（内存泄漏）
- `addEventListener` 在 cleanup 里未对应 `removeEventListener`
- 直接修改 state（应通过 `setState`/setter）
- 列表 `key` 用 `index` 且列表会增删重排；同层不同列表复用相同 key
- 受控/非受控混用（`value` 与 `defaultValue` 并存，或 `value` 从有值变 `undefined`）
- Context Provider 的 `value` 对象未 `useMemo` 导致全局重绘；`value` 内函数未 `useCallback` 导致子组件 memo 失效

**性能/稳定性**
- 渲染内匿名函数/对象传入 memo 组件导致 memo 失效
- 依赖数组中存在"永远是新引用"的对象（死循环风险）

**TS/安全**
- `any` 滥用、非空断言 `!` 风险
- `dangerouslySetInnerHTML` 缺少净化
- Props 类型缺失或过宽

### 🟡 建议修改

- **组件设计**：单文件职责过重；props drilling 过深；副作用混入纯展示组件
- **状态管理**：可用派生状态却额外 `useState`；异步无 loading/error 处理
- **可访问性**：交互控件缺 `aria-label`；图片缺 `alt`；仅靠颜色传达状态

### 🟢 可选优化

- 魔法数字/字符串；注释与实现不符；可抽成自定义 Hook 的重复逻辑
- 命名与文件位置是否符合仓库惯例

---

## 输出格式

**有问题时**，按优先级分组输出，每条包含：问题说明（文件 + 行号）+ Before/After 代码块：

```tsx
// Before
...
// After
...
```

末尾一句整体评估，例如：「逻辑正确，需先修 useEffect 依赖再提交。」

**无问题时**，直接输出：

```
✅ 审查通过。

git commit -m "type(scope): 描述"

## 改了什么
...
## 关键文件
...
## 破坏性变更
- 无
```

---

## 审查原则

- **具体**：文件 + 行号，不说「有些地方可以优化」
- **有依据**：说明为何是问题及潜在后果
- **不过度**：仅 typo、纯样式微调时快速确认即可，不硬找问题

---

## 特殊场景

| 场景 | 重点 |
|------|------|
| 纯样式/CSS | 响应式断点、设计 token 一致性、布局稳定性（CLS） |
| 新增 API 调用 | 错误处理、loading、请求竞态 |
| 重构 | 行为是否与重构前一致、调用点是否遗漏 |
| package.json 新依赖 | 维护情况、bundle 体积、是否有更轻替代 |

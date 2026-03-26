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

### Step 1：获取暂存区变更

若用户未提供 diff，在仓库根目录执行：

```bash
git diff --cached
git diff --cached --stat
git log --oneline -5
```

- 第一份：完整审查材料  
- `--stat`：文件与改动量概览  
- `git log`：最近提交节奏（命名与风格参考）

### Step 2：识别项目上下文

判断技术栈：读取仓库根目录 `package.json` 的 `dependencies` / `devDependencies`，关注 `react`、`typescript`、`next`、`vite`、`redux`、`zustand`、`@tanstack/react-query`、`tailwind` 等。

（若习惯命令行：`grep -E '"(react|typescript|next|vite|redux|zustand|react-query|tailwind)"' package.json`；在仅 PowerShell 的环境可读文件后用搜索代替。）

### Step 3：分层审查

按下方维度逐层检查。**发现高优先级问题立即在输出中标注**，不要等全部扫完再一次性汇总。

---

## 审查维度（React 专项）

### 高优先级 — 必须修复

**React 核心**

- Hook 规则：条件/循环内调用 Hook；在组件外误用 Hook  
- `useEffect` 依赖数组缺失或错误（无限循环、stale closure）  
- 直接改 state（应通过 `setState`/setter）  
- 列表 `key` 用 `index` 且列表会增删重排  
- 渲染路径与 Hook 顺序异常  

**性能**

- 每次渲染新建对象/函数传入子组件且子组件会因此重渲染（考虑 `useMemo`/`useCallback` 或结构拆分）  
- 大列表无虚拟化（若项目已有虚拟列表模式，对照一致性）  
- 重计算无 `useMemo`（且可观测到性能或稳定性问题）  

**TypeScript**

- 滥用 `any`  
- 对可能为 null/undefined 的值滥用非空断言 `!`  
- Props 类型缺失或过宽  

### 中优先级 — 建议修改

**组件设计**：单文件职责过重（例如明显混杂且远超约 150 行无拆分）；props drilling 过深；副作用塞进纯展示组件  

**状态管理**：可用派生状态却额外 `useState`；多个强相关 state 未合并；异步无 loading/error  

**可访问性**：交互控件缺 `aria-label`；图片缺 `alt`；仅靠颜色传达状态  

### 低优先级 — 可选优化

**代码质量**：魔法数字/字符串；注释与实现不符；可抽成自定义 Hook 的重复逻辑  

**项目规范**：命名（组件 PascalCase、函数 camelCase）、文件位置是否与仓库惯例一致  

---

## 输出格式

### 有问题时

结构要求：

- 一级标题：`## Code Review — [文件名或功能描述]`
- `### 必须修复（X 项）`：每条含 **问题标题**、`文件：` 与行号、`问题：` 说明；`修改建议：` 后紧跟独立 tsx 代码块（`// Before` / `// After`）
- `### 建议修改（X 项）`、`### 可选优化（X 项）`：同上分级，条数与标题一致
- 文末分隔线 + `整体评估：` 一句话（例如「逻辑正确，需先修 useEffect 依赖再提交」）

修改建议代码块示例（单独成块，勿嵌套在其他围栏内）：

```tsx
// Before
...
// After
...
```

### 无问题时

- `## Code Review — [描述]`
- 正文：`代码质量良好，可以提交。`
- `亮点：` 可选，一两句即可

输出中可使用 🔴🟡🟢 与「必须修复 / 建议修改 / 可选优化」对应，与上文维度一致。

---

## 审查态度原则

- **具体**：文件 + 行号（或 hunk 上下文），避免「有些地方可以优化」  
- **有依据**：说明为何是问题，不只说「不好」  
- **分级**：高优先级写清后果；低优先级给建议、不施压  
- **简洁**：每条尽量控制在约 5 行内；复杂处给 Before/After  
- **不过度**：仅 typo、纯样式微调时快速确认即可，不硬找问题  

---

## 特殊场景

| 场景 | 重点 |
|------|------|
| 纯样式/CSS | 响应式断点、设计 token/CSS 变量一致性、布局稳定性（CLS） |
| 新增 API 调用 | 错误处理、loading、请求竞态（旧响应覆盖新请求） |
| 重构 | 行为是否与重构前一致、调用点是否遗漏 |
| package.json 新依赖 | 维护情况、bundle 体积、是否有更轻替代 |

---

## 附加资源

完整检查清单与示例句式见 [reference.md](reference.md)。

# React Git Review — 参考清单

与 [SKILL.md](SKILL.md) 配合使用；审查时以 SKILL 为主，此处为审查指标的展开说明与备忘。

## 1. 深入审查准则 (详情展开)

### 🔴 必须修复 (Blocking)

**React**:
- Hook 仅在函数组件或自定义 Hook 顶层调用。
- `useEffect` 中使用的外部值应出现在依赖数组中；空数组仅当仅需挂载一次且内部不依赖变化中的闭包值。
- 列表 key：稳定 id 优于 index（动态列表尤其）。

**性能**:
- 子组件 `React.memo` 时，传入的 props 引用稳定性更重要。
- 虚拟化：长列表考虑 `react-window` / 项目既有方案。

**TS**:
- `unknown` + 收窄 优于 裸 `any`。
- 可选链 `?.` / 显式判空 优于 盲目使用非空断言 `!`。

### 🟡 建议修改 (Optimization)

**设计与逻辑**:
- Context / 状态库：仅在 props drilling 明显或跨层共享时引入，避免过早抽象。
- 异步：`finally` 中结束 loading 状态；错误抛出需用户可感知或可被记录。

### 🟢 可选优化 (Style)

**规范**:
- 常量集中到 `constants` 或与 feature 同目录的 `constants.ts` 文件中。
- 自定义 Hook 命名以 `use` 开头，语义与返回值需保持稳定。

## 2. 优先级对照指南

将上述详细准则与 `SKILL.md` 的输出格式结合，在回复中直接使用统一的标识：

- 🔴 **必须修复 (Blocking)** -> 对应上述高优先级展开内容
- 🟡 **建议修改 (Optimization)** -> 对应上述中优先级展开内容
- 🟢 **可选优化 (Style)** -> 对应上述低优先级展开内容

# React Git Review — 参考清单

与 [SKILL.md](SKILL.md) 配合使用；审查时以 SKILL 为主，此处为展开说明与备忘。

## 高优先级展开

**React**

- Hook 仅在函数组件或自定义 Hook 顶层调用  
- `useEffect` 中使用的外部值应出现在依赖数组中；空数组仅当仅需挂载一次且内部不依赖变化中的闭包值  
- 列表 key：稳定 id 优于 index（动态列表尤其）  

**性能**

- 子组件 `React.memo` 时，传入的 props 引用稳定性更重要  
- 虚拟化：长列表考虑 `react-window` / 项目既有方案  

**TS**

- `unknown` + 收窄 优于 裸 `any`  
- 可选链 `?.` / 显式判空 优于 盲目 `!`  

## 中优先级展开

- Context / 状态库：仅在 drilling 明显或跨层共享时引入，避免过早抽象  
- 异步：`finally` 中结束 loading；错误需用户可感知或可记录  

## 低优先级展开

- 常量集中到 `constants` 或与 feature 同目录的 `constants.ts`  
- 自定义 Hook 命名以 `use` 开头，语义与返回值稳定  

## 输出标题别名（可选）

在回复中可使用：

- 🔴 必须修复  
- 🟡 建议修改  
- 🟢 可选优化  

与 SKILL 中的「高 / 中 / 低」优先级一一对应。

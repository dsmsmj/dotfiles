# Proven Patterns

## Data fetching（Next.js）
Server Component 直接 async/await，不用 useEffect + fetch。
Client 侧用 TanStack Query，key 格式：['resource', id, filters]

## Error handling
Result 模式：返回 { data, error }，不 throw。
边界用 Next.js error.tsx 兜底。

## Form → API 流程
RHF 收集 → Zod parse（client）→ fetch → Zod parse（server）→ DB
两端用同一个 schema，放 lib/validators/xxx.ts

## 组件拆分原则
超过 150 行就拆。拆分信号：
- 有自己的状态 → 独立组件
- 可以被复用 → 放 components/ui/
- 业务逻辑 → 放 components/features/[domain]/

## API 设计
Route Handler 只做：validate → call service → return response
业务逻辑全在 services/，数据访问全在 repositories/

## 重构顺序
1. 加测试覆盖当前行为
2. 重构
3. 测试通过 = 完成
跳过步骤1时，明确告诉我风险。

## Python 脚本结构
typer app → 参数验证 → 业务函数（纯函数，可测试）→ 副作用最后执行
错误用 typer.echo(err, err=True) + raise typer.Exit(1)

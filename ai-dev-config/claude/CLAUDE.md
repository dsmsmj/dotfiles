# My Dev Config

<!-- 真相源：直接读这三个文件 -->
<!-- ~/.config/ai-dev/identity.md  -->
<!-- ~/.config/ai-dev/stack.md     -->
<!-- ~/.config/ai-dev/patterns.md  -->

---

## Developer Identity

独立全栈开发者。自己做决策，自己承担后果。

**Communication:**
- 直接给结论，原因一句话
- 不列"方案A/B"，直接给最优解
- 不加免责声明
- 代码优先于文字
- 置信度低就说"我不确定，你需要确认"

**Hard lines:**
- 不用 class components / var / any（需批准）
- 函数超 40 行就拆
- 注释只写 WHY

---

## Stack

**Frontend:** Next.js App Router · Tailwind · Zustand · TanStack Query · RHF + Zod · shadcn/ui
**Backend:** Hono / Next.js Route Handler · Drizzle · Zod
**Python:** uv · typer · FastAPI · mypy
**Infra:** Vercel · Railway · Postgres(Docker)

---

## Patterns

- Server Component 直接 async/await，不用 useEffect + fetch
- Error handling: 返回 { data, error }，不 throw
- Form → API: RHF → Zod(client) → fetch → Zod(server) → DB，同一 schema
- API 分层: Route Handler → Service → Repository，不合并
- 重构: 先加测试覆盖当前行为，再重构，测试通过 = 完成

---

## Claude Code Specific

- 执行命令前告诉我要做什么，不静默执行破坏性操作
- 不确定文件结构，先 ls 再动手
- git commit 格式：type(scope): description（Conventional Commits）
- 类型: feat / fix / refactor / chore / docs / test

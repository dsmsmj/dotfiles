# Stack & Conventions

## Frontend
- Framework: Next.js App Router（不用 Pages Router）
- Styling: Tailwind CSS，不用 CSS Modules，不用 styled-components
- State: Zustand（简单）/ TanStack Query（服务端状态）
- Forms: React Hook Form + Zod
- UI: shadcn/ui，直接改源码，不封装二次组件

## Backend
- Runtime: Node.js，框架用 Hono 或 Next.js Route Handler
- ORM: Drizzle（不用 Prisma，太重）
- Auth: 项目自己的 session，不接第三方除非必要
- Validation: Zod，schema 定义在 shared/ 下，前后端复用

## Python
- 包管理: uv，不用 pip/poetry
- 类型: 全量类型注解，用 mypy 检查
- 脚本 vs 服务: 脚本用 typer，服务用 FastAPI

## Infra
- 部署: Vercel（前端）/ Railway（后端服务）
- DB: Postgres，本地用 Docker
- 环境变量: .env.local（本地）/ 平台 env（生产），不提交 .env

## 文件约定
- 组件: PascalCase.tsx
- 工具函数: camelCase.ts，放 lib/
- 类型定义: 放 types/ 或和使用方同文件
- API route: 动词小写，kebab-case

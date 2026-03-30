# Stack & Conventions

## Frontend
- Framework: Next.js App Router (not Pages Router)
- Styling: Tailwind CSS; no CSS Modules or styled-components
- State: Zustand (local) / TanStack Query (server/cache)
- Forms: React Hook Form + Zod
- UI: shadcn/ui—edit source in place; avoid wrapper components

## Backend
- Runtime: Node.js with Hono or Next.js Route Handlers
- ORM: Drizzle (avoid Prisma—too heavy for this setup)
- Auth: app-owned sessions; no third-party auth unless necessary
- Validation: Zod schemas in `shared/`, reused client and server

## Python
- Packaging: `uv` (not pip/poetry by default)
- Types: full annotations + mypy
- Scripts vs services: Typer for CLI, FastAPI for services

## Infra
- Deploy: Vercel (frontend) / Railway (backend services)
- DB: Postgres; local via Docker
- Env: `.env.local` locally; platform env in prod—never commit secrets

## File conventions
- Components: `PascalCase.tsx`
- Utilities: `camelCase.ts` under `lib/`
- Types: `types/` or colocated with usage
- API routes: lowercase verbs, kebab-case paths

# Proven Patterns

## Data fetching (Next.js)
- Server Components: async/await in the component—no `useEffect` + `fetch` for initial data
- Client: TanStack Query with keys like `['resource', id, filters]`

## Error handling
- Result style: return `{ data, error }`; avoid throwing for expected failures
- Route-level failures: rely on `error.tsx` where appropriate

## Form → API
RHF → Zod (client) → fetch → Zod (server) → DB  
One schema file under `lib/validators/<feature>.ts` shared both ends.

## Component splits
Split around ~150 lines. Signals:
- Own state boundary → new component
- Reusable visual → `components/ui/`
- Domain logic → `components/features/<domain>/`

## API shape
Route handler: validate → service → response  
Business logic stays in `services/`; data access in `repositories/`.

## Refactor order
1. Add tests for current behavior
2. Refactor
3. Green tests = done  
If step 1 is skipped, call out the risk explicitly.

## Python CLI layout
Typer app → validated args → pure business functions → side effects last  
Errors: `typer.echo(err, err=True)` + `raise typer.Exit(1)`

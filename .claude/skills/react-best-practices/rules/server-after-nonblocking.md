---
title: Non-Blocking Background Tasks After Response
impact: MEDIUM
impactDescription: faster response times
tags: server, async, logging, analytics, side-effects, background-tasks
---

## Non-Blocking Background Tasks After Response

Schedule non-critical work (logging, analytics, notifications) to execute after the response is sent, preventing side effects from blocking the response.

**Incorrect (blocks response):**

```tsx
import { logUserAction } from './utils'

export async function POST(request: Request) {
  // Perform mutation
  await updateDatabase(request)
  
  // Logging blocks the response
  const userAgent = request.headers.get('user-agent') || 'unknown'
  await logUserAction({ userAgent })
  
  return new Response(JSON.stringify({ status: 'success' }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  })
}
```

**Correct (non-blocking with setImmediate / queueMicrotask):**

```tsx
import { logUserAction } from './utils'

export async function POST(request: Request) {
  // Perform mutation
  await updateDatabase(request)
  
  // Capture data before sending response
  const userAgent = request.headers.get('user-agent') || 'unknown'
  
  // Schedule logging to run after current execution
  // Use setImmediate (Node.js) or queueMicrotask (browser/universal)
  queueMicrotask(() => {
    logUserAction({ userAgent })
  })
  
  return new Response(JSON.stringify({ status: 'success' }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  })
}
```

**Alternative: using waitUntil (edge runtimes / Cloudflare Workers):**

```tsx
export async function POST(request: Request, ctx: ExecutionContext) {
  await updateDatabase(request)
  
  const userAgent = request.headers.get('user-agent') || 'unknown'
  
  // Keeps the worker alive to complete background work
  ctx.waitUntil(logUserAction({ userAgent }))
  
  return new Response(JSON.stringify({ status: 'success' }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  })
}
```

The response is sent immediately while logging happens in the background.

**Common use cases:**

- Analytics tracking
- Audit logging
- Sending notifications
- Cache invalidation
- Cleanup tasks

**Framework-specific APIs:**

- **Next.js:** Use `after()` from `next/server` (Next.js 15+)
- **Cloudflare Workers:** Use `ctx.waitUntil()`
- **Express/Koa:** Send response first, then run async work
- **Node.js:** Use `setImmediate()` or `process.nextTick()`

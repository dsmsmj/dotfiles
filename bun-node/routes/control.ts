import { json, badRequest } from '../lib/sse.ts'
import { runtime, controllers, handles, handleKey, getOrCreateHandle } from '../lib/runtime.ts'

async function readJsonBody(req: Request): Promise<unknown> {
  try { return await req.json() } catch { return null }
}

function str(obj: unknown, key: string): string | null {
  if (typeof obj !== 'object' || obj === null) return null
  const v = (obj as Record<string, unknown>)[key]
  return typeof v === 'string' ? v : null
}

export async function handleControl(req: Request, url: URL): Promise<Response | null> {

  // GET /api/health — runtime health + doctor report
  if (req.method === 'GET' && url.pathname === '/api/health') {
    const healthy = runtime.isHealthy()
    if (!healthy) {
      try {
        const report = await runtime.doctor()
        return json({ ...report, ok: false }, { status: 503 })
      } catch (err) {
        return json({ ok: false, message: String(err) }, { status: 503 })
      }
    }
    return json({ ok: true, message: 'runtime healthy' })
  }

  // GET /api/capabilities — what the runtime supports
  if (req.method === 'GET' && url.pathname === '/api/capabilities') {
    const caps = runtime.getCapabilities()
    return json(caps)
  }

  // GET /api/status?agent=&sessionId=
  if (req.method === 'GET' && url.pathname === '/api/status') {
    const agent = url.searchParams.get('agent') ?? 'qwen'
    const sessionId = url.searchParams.get('sessionId') ?? 'default'
    const key = handleKey(agent, sessionId)
    const handle = handles.get(key)
    if (!handle) return json({ summary: 'no active session', backendSessionId: null, agentSessionId: null })
    try {
      const status = await runtime.getStatus({ handle })
      return json(status)
    } catch (err) {
      return json({ error: String(err) }, { status: 500 })
    }
  }

  // POST /api/cancel  { agent, sessionId }
  if (req.method === 'POST' && url.pathname === '/api/cancel') {
    const body = await readJsonBody(req)
    const agent = str(body, 'agent') ?? 'qwen'
    const sessionId = str(body, 'sessionId') ?? 'default'
    const key = handleKey(agent, sessionId)

    // Abort active SSE stream first
    controllers.get(key)?.abort()

    // Also notify the runtime
    const handle = handles.get(key)
    if (handle) {
      try { await runtime.cancel({ handle, reason: 'user cancelled' }) } catch { /* best-effort */ }
    }

    return json({ ok: true })
  }

  // POST /api/mode  { agent, sessionId, mode }
  if (req.method === 'POST' && url.pathname === '/api/mode') {
    const body = await readJsonBody(req)
    const agent = str(body, 'agent') ?? 'qwen'
    const sessionId = str(body, 'sessionId') ?? 'default'
    const mode = str(body, 'mode')
    if (!mode?.trim()) return badRequest('mode required')

    const handle = await getOrCreateHandle(agent, sessionId)
    try {
      await runtime.setMode({ handle, mode })
      return json({ ok: true, mode })
    } catch (err) {
      return json({ error: String(err) }, { status: 500 })
    }
  }

  // POST /api/config  { agent, sessionId, key, value }
  if (req.method === 'POST' && url.pathname === '/api/config') {
    const body = await readJsonBody(req)
    const agent = str(body, 'agent') ?? 'qwen'
    const sessionId = str(body, 'sessionId') ?? 'default'
    const key = str(body, 'key')
    const value = str(body, 'value')
    if (!key?.trim()) return badRequest('key required')
    if (value === null) return badRequest('value required')

    const handle = await getOrCreateHandle(agent, sessionId)
    try {
      await runtime.setConfigOption({ handle, key, value })
      return json({ ok: true, key, value })
    } catch (err) {
      return json({ error: String(err) }, { status: 500 })
    }
  }

  return null
}

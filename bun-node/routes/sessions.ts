import { json, badRequest } from '../lib/sse.ts'
import {
  runtime,
  sessionStore,
  handles,
  handleKey,
  getOrCreateHandle,
} from '../lib/runtime.ts'
import { listSessions, loadSessionMessages } from '../lib/sessions.ts'

async function readJsonBody(req: Request): Promise<unknown> {
  try { return await req.json() } catch { return null }
}

function str(obj: unknown, key: string): string | null {
  if (typeof obj !== 'object' || obj === null) return null
  const v = (obj as Record<string, unknown>)[key]
  return typeof v === 'string' ? v : null
}

export async function handleSessions(req: Request, url: URL): Promise<Response | null> {

  // GET /api/sessions?agent=
  if (req.method === 'GET' && url.pathname === '/api/sessions') {
    const agent = url.searchParams.get('agent') ?? 'claude'
    return json({ sessions: listSessions(agent) })
  }

  // GET /api/session-messages?agent=&sessionId=
  if (req.method === 'GET' && url.pathname === '/api/session-messages') {
    const agent = url.searchParams.get('agent') ?? 'claude'
    const sessionId = url.searchParams.get('sessionId') ?? ''
    if (!sessionId.trim()) return json({ messages: [] })
    return json({ messages: loadSessionMessages(agent, sessionId) })
  }

  // GET /api/session-state?agent=&sessionId=
  if (req.method === 'GET' && url.pathname === '/api/session-state') {
    const agent = url.searchParams.get('agent') ?? 'claude'
    const sessionId = url.searchParams.get('sessionId') ?? 'default'
    const key = handleKey(agent, sessionId)
    const handle = handles.get(key)
    try {
      const record = handle?.acpxRecordId
        ? await sessionStore.load(handle.acpxRecordId)
        : undefined
      return json({
        availableCommands: record?.acpx?.available_commands ?? [],
        currentMode: record?.acpx?.current_mode_id ?? null,
        currentModel: record?.acpx?.current_model_id ?? null,
      })
    } catch {
      return json({ availableCommands: [], currentMode: null, currentModel: null })
    }
  }

  // POST /api/sessions/new  { agent, sessionId }
  if (req.method === 'POST' && url.pathname === '/api/sessions/new') {
    const body = await readJsonBody(req)
    const agent = str(body, 'agent') ?? 'claude'
    const sessionId = str(body, 'sessionId')
    if (!sessionId?.trim()) return badRequest('sessionId required')
    try {
      await getOrCreateHandle(agent, sessionId)
      return json({ ok: true, sessionId })
    } catch (err) {
      return json({ error: String(err) }, { status: 500 })
    }
  }

  // POST /api/sessions/close  { agent, sessionId }
  if (req.method === 'POST' && url.pathname === '/api/sessions/close') {
    const body = await readJsonBody(req)
    const agent = str(body, 'agent') ?? 'claude'
    const sessionId = str(body, 'sessionId')
    if (!sessionId?.trim()) return badRequest('sessionId required')
    const key = handleKey(agent, sessionId)
    const handle = handles.get(key)
    if (handle) {
      try {
        await runtime.close({ handle, reason: 'user closed' })
      } catch { /* best-effort */ }
      handles.delete(key)
    }
    return json({ ok: true })
  }

  return null
}

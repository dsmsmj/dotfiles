import { randomUUID } from 'node:crypto'
import { sseEvent, sseHeaders, json } from '../lib/sse.ts'
import { runtime, controllers, handleKey, getOrCreateHandle } from '../lib/runtime.ts'

async function readJsonBody(req: Request): Promise<unknown> {
  try { return await req.json() } catch { return null }
}

function str(obj: unknown, key: string): string | null {
  if (typeof obj !== 'object' || obj === null) return null
  const v = (obj as Record<string, unknown>)[key]
  return typeof v === 'string' ? v : null
}

function num(obj: unknown, key: string): number | undefined {
  if (typeof obj !== 'object' || obj === null) return undefined
  const v = (obj as Record<string, unknown>)[key]
  return typeof v === 'number' ? v : undefined
}

/**
 * POST /api/run  { agent, sessionId, prompt, timeoutMs? }
 * Streams events as SSE: status | out | tool | done | error
 */
export async function handleRun(
  req: Request,
  url: URL,
  srv: { timeout(req: Request, ms: number): void },
): Promise<Response | null> {
  if (req.method !== 'POST' || url.pathname !== '/api/run') return null

  const body = await readJsonBody(req)
  const agent = str(body, 'agent') ?? 'qwen'
  const sessionId = str(body, 'sessionId') ?? 'default'
  const prompt = str(body, 'prompt') ?? ''
  const timeoutMs = num(body, 'timeoutMs')

  const handle = await getOrCreateHandle(agent, sessionId)
  const key = handleKey(agent, sessionId)

  const controller = new AbortController()
  controllers.set(key, controller)

  let closed = false

  const stream = new ReadableStream({
    start(ctrl) {
      const heartbeat = setInterval(() => {
        if (!closed) ctrl.enqueue(': ping\n\n')
      }, 8_000)

      const cleanup = () => {
        if (closed) return
        closed = true
        clearInterval(heartbeat)
        controllers.delete(key)
        try { ctrl.close() } catch { /* ignore */ }
      }

      ;(async () => {
        try {
          ctrl.enqueue(sseEvent('status', 'running'))
          for await (const ev of runtime.runTurn({
            handle,
            text: prompt,
            mode: 'prompt',
            requestId: randomUUID(),
            timeoutMs,
            signal: controller.signal,
          })) {
            if (closed) break
            switch (ev.type) {
              case 'text_delta':
                ctrl.enqueue(sseEvent('out', ev.text, ev.tag ? { tag: ev.tag } : undefined))
                break
              case 'status':
                ctrl.enqueue(sseEvent('status', ev.text, ev.tag ? { tag: ev.tag } : undefined))
                break
              case 'tool_call':
                ctrl.enqueue(sseEvent('tool', ev.text, {
                  ...(ev.toolCallId && { toolCallId: ev.toolCallId }),
                  ...(ev.status && { toolStatus: ev.status }),
                  ...(ev.tag && { tag: ev.tag }),
                }))
                break
              case 'done':
                ctrl.enqueue(sseEvent('done', ev.stopReason ?? ''))
                break
              case 'error':
                ctrl.enqueue(sseEvent('error', ev.message, ev.code ? { code: ev.code } : undefined))
                break
            }
          }
        } catch (err) {
          try { ctrl.enqueue(sseEvent('error', String(err))) } catch { /* ignore */ }
        } finally {
          cleanup()
        }
      })()
    },
    cancel() {
      controller.abort()
      closed = true
      controllers.delete(key)
    },
  })

  srv.timeout(req, 0)
  return new Response(stream, { headers: sseHeaders() })
}

/**
 * POST /api/exec  { agent, prompt, cwd?, timeoutMs? }
 * One-shot execution — creates a throwaway session, streams SSE, then closes
 */
export async function handleExec(
  req: Request,
  url: URL,
  srv: { timeout(req: Request, ms: number): void },
): Promise<Response | null> {
  if (req.method !== 'POST' || url.pathname !== '/api/exec') return null

  const body = await readJsonBody(req)
  const agent = str(body, 'agent') ?? 'qwen'
  const prompt = str(body, 'prompt') ?? ''
  const timeoutMs = num(body, 'timeoutMs')

  let handle: Awaited<ReturnType<typeof runtime.ensureSession>>
  try {
    handle = await runtime.ensureSession({
      sessionKey: `exec-${randomUUID()}`,
      agent,
      mode: 'oneshot',
    })
  } catch (err) {
    return json({ error: String(err) }, { status: 500 })
  }

  const controller = new AbortController()
  let closed = false

  const stream = new ReadableStream({
    start(ctrl) {
      const heartbeat = setInterval(() => {
        if (!closed) ctrl.enqueue(': ping\n\n')
      }, 8_000)

      const cleanup = async () => {
        if (closed) return
        closed = true
        clearInterval(heartbeat)
        try { await runtime.close({ handle, reason: 'exec complete' }) } catch { /* ignore */ }
        try { ctrl.close() } catch { /* ignore */ }
      }

      ;(async () => {
        try {
          ctrl.enqueue(sseEvent('status', 'running'))
          for await (const ev of runtime.runTurn({
            handle,
            text: prompt,
            mode: 'prompt',
            requestId: randomUUID(),
            timeoutMs,
            signal: controller.signal,
          })) {
            if (closed) break
            switch (ev.type) {
              case 'text_delta':
                ctrl.enqueue(sseEvent('out', ev.text))
                break
              case 'status':
                ctrl.enqueue(sseEvent('status', ev.text))
                break
              case 'tool_call':
                ctrl.enqueue(sseEvent('tool', ev.text, {
                  ...(ev.toolCallId && { toolCallId: ev.toolCallId }),
                  ...(ev.status && { toolStatus: ev.status }),
                }))
                break
              case 'done':
                ctrl.enqueue(sseEvent('done', ev.stopReason ?? ''))
                break
              case 'error':
                ctrl.enqueue(sseEvent('error', ev.message))
                break
            }
          }
        } catch (err) {
          try { ctrl.enqueue(sseEvent('error', String(err))) } catch { /* ignore */ }
        } finally {
          await cleanup()
        }
      })()
    },
    cancel() {
      controller.abort()
      closed = true
      runtime.close({ handle, reason: 'exec cancelled' }).catch(() => {})
    },
  })

  srv.timeout(req, 0)
  return new Response(stream, { headers: sseHeaders() })
}

import type { Agent, Message } from '../types'

export type SessionState = {
  availableCommands: string[]
  currentMode: string | null
  currentModel: string | null
}

export type RuntimeStatus = {
  summary?: string
  backendSessionId?: string | null
  agentSessionId?: string | null
  details?: Record<string, unknown>
}

export type RuntimeCapabilities = {
  controls: string[]
  configOptionKeys?: string[]
}

export type HealthReport = {
  ok: boolean
  message: string
  installCommand?: string
  details?: string[]
}

export type SseEvent = {
  type: string
  data: string
  toolCallId?: string
  toolStatus?: string
  tag?: string
  code?: string
}

// All fetch calls go through here so base URL is one place to change
const BASE = ''

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText })) as { error?: string }
    throw new Error(err.error ?? res.statusText)
  }
  return res.json() as Promise<T>
}

async function get<T>(path: string, params?: Record<string, string>): Promise<T> {
  const url = new URL(`${BASE}${path}`, location.href)
  if (params) Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v))
  const res = await fetch(url.toString())
  if (!res.ok) throw new Error(res.statusText)
  return res.json() as Promise<T>
}

export const api = {
  sessions: {
    list: (agent: Agent) =>
      get<{ sessions: string[] }>('/api/sessions', { agent }),

    messages: (agent: Agent, sessionId: string) =>
      get<{ messages: Message[] }>('/api/session-messages', { agent, sessionId }),

    state: (agent: Agent, sessionId: string) =>
      get<SessionState>('/api/session-state', { agent, sessionId }),

    new: (agent: Agent, sessionId: string) =>
      post<{ ok: boolean; sessionId: string }>('/api/sessions/new', { agent, sessionId }),

    close: (agent: Agent, sessionId: string) =>
      post<{ ok: boolean }>('/api/sessions/close', { agent, sessionId }),
  },

  images: {
    list: (sessionId: string) =>
      get<{ images: string[] }>('/api/images', { sessionId }),
  },

  health: () =>
    get<HealthReport>('/api/health'),

  capabilities: () =>
    get<RuntimeCapabilities>('/api/capabilities'),

  status: (agent: Agent, sessionId: string) =>
    get<RuntimeStatus>('/api/status', { agent, sessionId }),

  cancel: (agent: Agent, sessionId: string) =>
    post<{ ok: boolean }>('/api/cancel', { agent, sessionId }),

  mode: (agent: Agent, sessionId: string, mode: string) =>
    post<{ ok: boolean; mode: string }>('/api/mode', { agent, sessionId, mode }),

  config: (agent: Agent, sessionId: string, key: string, value: string) =>
    post<{ ok: boolean; key: string; value: string }>('/api/config', { agent, sessionId, key, value }),

  /**
   * Returns a native fetch Response with a ReadableStream body.
   * Caller is responsible for reading the SSE stream.
   */
  run: (agent: Agent, sessionId: string, prompt: string, timeoutMs?: number): Promise<Response> =>
    fetch('/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent, sessionId, prompt, timeoutMs }),
    }),

  exec: (agent: Agent, prompt: string, timeoutMs?: number): Promise<Response> =>
    fetch('/api/exec', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent, prompt, timeoutMs }),
    }),
}

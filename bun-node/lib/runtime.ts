import { mkdirSync } from 'node:fs'
import { join, resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import {
  createAcpRuntime,
  createAgentRegistry,
  createFileSessionStore,
} from 'acpx/runtime'
import type { AcpRuntimeHandle, AcpSessionStore } from 'acpx/runtime'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export const PROJECT_ROOT =
  process.env.ACPX_PROJECT_ROOT ?? resolve(__dirname, '..')

export const DATA_ROOT =
  process.env.ACPX_DATA_ROOT ?? resolve(__dirname, '..', 'data')

export const PORT = Number(process.env.PORT ?? 9003)

// Ensure required directories exist
mkdirSync(DATA_ROOT, { recursive: true })
mkdirSync(join(DATA_ROOT, '.acpx'), { recursive: true })
mkdirSync(join(DATA_ROOT, '.acpx', 'sessions'), { recursive: true })
mkdirSync(join(DATA_ROOT, 'sessions'), { recursive: true })

export const sessionStore: AcpSessionStore = createFileSessionStore({
  stateDir: join(DATA_ROOT, '.acpx'),
})

export const agentRegistry = createAgentRegistry()
console.log('PROJECT_ROOT',PROJECT_ROOT)
export const runtime = createAcpRuntime({
  cwd: PROJECT_ROOT,
  sessionStore,
  agentRegistry,
  permissionMode: 'approve-all',
})

// In-memory handle + controller maps (process lifetime)
export const handles = new Map<string, AcpRuntimeHandle>()
export const controllers = new Map<string, AbortController>()

export function handleKey(agent: string, sessionId: string): string {
  return `${agent}:${sessionId}`
}

export async function getOrCreateHandle(agent: string, sessionId: string): Promise<AcpRuntimeHandle> {
  const key = handleKey(agent, sessionId)
  let handle = handles.get(key)
  if (!handle) {
    handle = await runtime.ensureSession({
      sessionKey: sessionId,
      agent,
      mode: 'persistent',
      cwd: PROJECT_ROOT,
    })
    handles.set(key, handle)
  }
  return handle
}

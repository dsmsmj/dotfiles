import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs'
import { join, extname, normalize } from 'node:path'
import { agentRegistry, DATA_ROOT } from './runtime.ts'
import type { ImageArtifact, ImageGenerationResult, TextArtifact, UiMessage, UiSegment } from '../types.ts'

const IMAGE_EXTS = new Set(['.png', '.jpg', '.jpeg', '.gif', '.webp'])

export const MIME_MAP: Record<string, string> = {
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.webp': 'image/webp',
}

export function listSessions(agent: string): string[] {
  const sessionsDir = join(DATA_ROOT, '.acpx', 'sessions')
  if (!existsSync(sessionsDir)) return []
  const resolvedCommand = agentRegistry.resolve(agent)
  return readdirSync(sessionsDir)
    .filter(f => f.endsWith('.json') && statSync(join(sessionsDir, f)).isFile())
    .filter(f => {
      try {
        const raw = JSON.parse(readFileSync(join(sessionsDir, f), 'utf-8')) as { agent_command?: string }
        return raw.agent_command === resolvedCommand
      } catch {
        return false
      }
    })
    .map(f => f.slice(0, -5))
}

export function listImages(sessionId: string): string[] {
  const outputDir = join(DATA_ROOT, 'sessions', sessionId, 'output')
  if (!existsSync(outputDir)) return []
  return readdirSync(outputDir)
    .filter(f => IMAGE_EXTS.has(extname(f).toLowerCase()))
    .sort()
    .map(f => `/sessions/${sessionId}/output/${f}`)
}

function imageArtifactId(sessionId: string, fileName: string): string {
  return `img_${sessionId}_${fileName.replace(/[^a-zA-Z0-9]+/g, '_')}`
}

function maybeReadBase64(fullPath: string, includeData: boolean): Pick<ImageArtifact, 'encoding' | 'data'> {
  if (!includeData) return {}
  const bytes = readFileSync(fullPath)
  return {
    encoding: 'base64',
    data: Buffer.from(bytes).toString('base64'),
  }
}

export function listImageArtifacts(sessionId: string, includeData = false): ImageArtifact[] {
  const outputDir = join(DATA_ROOT, 'sessions', sessionId, 'output')
  if (!existsSync(outputDir)) return []

  return readdirSync(outputDir)
    .filter(fileName => IMAGE_EXTS.has(extname(fileName).toLowerCase()))
    .sort()
    .map(fileName => {
      const fullPath = join(outputDir, fileName)
      const stats = statSync(fullPath)
      const ext = extname(fileName).toLowerCase()

      return {
        id: imageArtifactId(sessionId, fileName),
        kind: 'image',
        mimeType: MIME_MAP[ext] ?? 'application/octet-stream',
        uri: `/sessions/${sessionId}/output/${fileName}`,
        fileName,
        sizeBytes: stats.size,
        metadata: {
          sessionId,
          source: 'session-output',
        },
        ...maybeReadBase64(fullPath, includeData),
      } satisfies ImageArtifact
    })
}

// Known text files produced by skills, in priority order.
// The first entry whose file exists is used as revisedPrompt.
const TEXT_ARTIFACT_FILES = [
  { fileName: 'design_concept.txt', role: 'concept' },
  { fileName: 'design_strategy.txt', role: 'strategy' },
] as const

function textArtifactId(sessionId: string, fileName: string): string {
  return `txt_${sessionId}_${fileName.replace(/[^a-zA-Z0-9]+/g, '_')}`
}

export function listTextArtifacts(sessionId: string): TextArtifact[] {
  const sessionDir = join(DATA_ROOT, 'sessions', sessionId)
  const artifacts: TextArtifact[] = []

  for (const { fileName, role } of TEXT_ARTIFACT_FILES) {
    const fullPath = join(sessionDir, fileName)
    if (!existsSync(fullPath) || !statSync(fullPath).isFile()) continue
    const text = readFileSync(fullPath, 'utf-8')
    if (!text.trim()) continue
    artifacts.push({
      id: textArtifactId(sessionId, fileName),
      kind: 'text',
      fileName,
      text,
      metadata: { sessionId, role, source: 'session-output' },
    })
  }

  // Include individual design plans from the design_plans/ subdir
  const plansDir = join(sessionDir, 'design_plans')
  if (existsSync(plansDir) && statSync(plansDir).isDirectory()) {
    const planFiles = readdirSync(plansDir)
      .filter(f => f.endsWith('.txt'))
      .sort()
    for (const fileName of planFiles) {
      const fullPath = join(plansDir, fileName)
      if (!statSync(fullPath).isFile()) continue
      const text = readFileSync(fullPath, 'utf-8')
      if (!text.trim()) continue
      const qualifiedName = `design_plans/${fileName}`
      artifacts.push({
        id: textArtifactId(sessionId, qualifiedName),
        kind: 'text',
        fileName: qualifiedName,
        text,
        metadata: { sessionId, role: 'plan', source: 'session-output' },
      })
    }
  }

  return artifacts
}

export function buildImageGenerationResult(sessionId: string, includeData = false): ImageGenerationResult {
  const imageArtifacts = listImageArtifacts(sessionId, includeData)
  const textArtifacts = listTextArtifacts(sessionId)

  // Use design_concept.txt as revisedPrompt if available
  const conceptArtifact = textArtifacts.find(a => a.fileName === 'design_concept.txt')

  const artifacts = [...imageArtifacts, ...textArtifacts]
  return {
    type: 'image_generation_result',
    status: imageArtifacts.length > 0 ? 'succeeded' : 'failed',
    revisedPrompt: conceptArtifact?.text,
    artifacts,
    notes: imageArtifacts.length > 0
      ? ['Returned session image and text artifacts as structured output.']
      : ['No generated images were found for this session.'],
  }
}

function extractUserContentText(content: unknown): string {
  if (!Array.isArray(content)) return ''
  return content
    .filter((b): b is Record<string, unknown> => typeof b === 'object' && b !== null)
    .filter(b => typeof b.Text === 'string')
    .map(b => b.Text as string)
    .join('')
}

function agentBlocksToSegments(content: unknown): UiSegment[] {
  if (!Array.isArray(content)) return []
  const segs: UiSegment[] = []
  for (const block of content) {
    if (typeof block !== 'object' || block === null) continue
    const b = block as Record<string, unknown>
    if ('Thinking' in b && b.Thinking && typeof b.Thinking === 'object') {
      const t = (b.Thinking as { text?: unknown }).text
      if (typeof t === 'string' && t.trim()) segs.push({ kind: 'status', text: t })
    } else if (typeof b.Text === 'string') {
      segs.push({ kind: 'text', text: b.Text })
    }
  }
  return segs
}

export function loadSessionMessages(agent: string, sessionId: string): UiMessage[] {
  const path = join(DATA_ROOT, '.acpx', 'sessions', `${sessionId}.json`)
  if (!existsSync(path)) return []
  let raw: unknown
  try {
    raw = JSON.parse(readFileSync(path, 'utf-8'))
  } catch {
    return []
  }
  if (typeof raw !== 'object' || raw === null) return []
  const rec = raw as { agent_command?: string; messages?: unknown }
  if (rec.agent_command !== agentRegistry.resolve(agent)) return []
  if (!Array.isArray(rec.messages)) return []

  const out: UiMessage[] = []
  for (let i = 0; i < rec.messages.length; i++) {
    const item = rec.messages[i]
    if (typeof item !== 'object' || item === null) continue
    const o = item as Record<string, unknown>
    if ('User' in o && o.User && typeof o.User === 'object') {
      const u = o.User as { id?: string; content?: unknown }
      out.push({
        id: typeof u.id === 'string' ? u.id : `u-${sessionId}-${i}`,
        role: 'user',
        content: extractUserContentText(u.content),
      })
    } else if ('Agent' in o && o.Agent && typeof o.Agent === 'object') {
      const a = o.Agent as { content?: unknown }
      const segs = agentBlocksToSegments(a.content)
      out.push({
        id: `a-${sessionId}-${i}`,
        role: 'assistant',
        content: segs.length > 0 ? segs : [{ kind: 'text', text: '' }],
      })
    }
  }
  return out
}

// Safe path join that prevents directory traversal under DATA_ROOT/sessions
export function safeSessionFilePath(rel: string): string | null {
  const cleaned = rel.replace(/^\/+/, '')
  const full = normalize(join(DATA_ROOT, 'sessions', cleaned))
  const base = normalize(join(DATA_ROOT, 'sessions') + '/')
  // Windows compat: normalize uses backslashes
  const fullNorm = full.replace(/\\/g, '/')
  const baseNorm = base.replace(/\\/g, '/')
  if (!fullNorm.startsWith(baseNorm)) return null
  return full
}

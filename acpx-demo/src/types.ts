export type Agent =
  | 'qwen'
  | 'claude'
  | 'gemini'
  | 'codex'
  | 'cursor'
  | 'copilot'
  | 'kimi'
  | 'trae'
  | 'pi'
  | 'openclaw'

export const AGENTS: readonly Agent[] = [
  'qwen',
  'claude',
  'gemini',
  'codex',
  'cursor',
  'copilot',
  'kimi',
  'trae',
  'pi',
  'openclaw',
] as const

export type Segment =
  | { kind: 'text'; text: string }
  | { kind: 'status'; text: string }
  | { kind: 'tool'; text: string; toolCallId?: string; toolStatus?: string }

export type Message = {
  id: string
  role: 'user' | 'assistant'
  // Plain string for user messages; segment array for assistant messages
  content: string | Segment[]
  isStreaming?: boolean
}

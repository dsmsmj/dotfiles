export type UiSegment =
  | { kind: 'text'; text: string }
  | { kind: 'status'; text: string }
  | { kind: 'tool'; text: string; toolCallId?: string; toolStatus?: string }

export type UiMessage = {
  id: string
  role: 'user' | 'assistant'
  content: string | UiSegment[]
}

export type SessionState = {
  availableCommands: string[]
  currentMode: string | null
  currentModel: string | null
}

export type SsePayload = {
  type: 'status' | 'out' | 'tool' | 'done' | 'error'
  data: string
  toolCallId?: string
  toolStatus?: string
  tag?: string
}

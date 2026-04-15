export type UiSegment =
  | { kind: 'text'; text: string }
  | { kind: 'status'; text: string }
  | { kind: 'tool'; text: string; toolCallId?: string; toolStatus?: string }

export type ArtifactKind = 'image' | 'text'

export type ArtifactEncoding = 'base64'

export type ImageArtifact = {
  id: string
  kind: 'image'
  mimeType: string
  uri: string
  fileName: string
  width?: number
  height?: number
  sizeBytes?: number
  encoding?: ArtifactEncoding
  data?: string
  metadata?: Record<string, unknown>
}

export type TextArtifact = {
  id: string
  kind: 'text'
  fileName: string
  text: string
  metadata?: Record<string, unknown>
}

export type Artifact = ImageArtifact | TextArtifact

export type ImageGenerationResult = {
  type: 'image_generation_result'
  status: 'succeeded' | 'failed'
  prompt?: string
  revisedPrompt?: string
  artifacts: Artifact[]
  notes?: string[]
}

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

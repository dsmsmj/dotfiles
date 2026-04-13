import { useState, useCallback, useRef } from 'react'
import { api } from '../api/client'
import { useStream } from './useStream'
import type { Agent, Message, Segment } from '../types'
import type { SessionState } from '../api/client'

let _id = 0
const uid = () => String(++_id)

/**
 * Encapsulates all session-level state and actions for one (agent, sessionId) pair.
 * App.tsx stays as a thin composition layer.
 */
export function useSession(agent: Agent, sessionId: string) {
  const [messages, setMessages] = useState<Message[]>([])
  const [images, setImages] = useState<string[]>([])
  const [sessionState, setSessionState] = useState<SessionState>({
    availableCommands: [],
    currentMode: null,
    currentModel: null,
  })
  const [isRunning, setIsRunning] = useState(false)

  const historyGenRef = useRef(0)
  const { start, abort } = useStream()

  const loadMessages = useCallback(async () => {
    if (!sessionId.trim()) { setMessages([]); return }
    const gen = ++historyGenRef.current
    try {
      const { messages: msgs } = await api.sessions.messages(agent, sessionId)
      if (gen !== historyGenRef.current) return
      setMessages(msgs ?? [])
    } catch {
      if (gen !== historyGenRef.current) return
      setMessages([])
    }
  }, [agent, sessionId])

  const loadImages = useCallback(async () => {
    try {
      const { images: imgs } = await api.images.list(sessionId)
      setImages(imgs ?? [])
    } catch { /* network not ready */ }
  }, [sessionId])

  const loadState = useCallback(async () => {
    if (!sessionId.trim()) return
    try {
      const state = await api.sessions.state(agent, sessionId)
      setSessionState(state)
    } catch { /* ignore */ }
  }, [agent, sessionId])

  const refreshAll = useCallback(() => {
    void loadMessages()
    void loadImages()
    void loadState()
  }, [loadMessages, loadImages, loadState])

  const cancel = useCallback(() => {
    abort()
    void api.cancel(agent, sessionId).catch(() => {})
    setIsRunning(false)
    setMessages(prev => prev.map(m => (m.isStreaming ? { ...m, isStreaming: false } : m)))
  }, [abort, agent, sessionId])

  const send = useCallback(async (prompt: string) => {
    if (isRunning || !prompt.trim()) return

    const userMsgId = uid()
    const assistantId = uid()

    setMessages(prev => [
      ...prev,
      { id: userMsgId, role: 'user', content: prompt },
      { id: assistantId, role: 'assistant', content: [] as Segment[], isStreaming: true },
    ])
    setIsRunning(true)

    const appendSeg = (seg: Segment) =>
      setMessages(prev =>
        prev.map(m => {
          if (m.id !== assistantId) return m
          const segs = Array.isArray(m.content) ? m.content : []
          const last = segs[segs.length - 1]
          if (last && last.kind === seg.kind && seg.kind === 'text') {
            return { ...m, content: [...segs.slice(0, -1), { ...last, text: last.text + seg.text }] }
          }
          return { ...m, content: [...segs, seg] }
        })
      )

    const appendOrUpdateTool = (text: string, toolCallId?: string, toolStatus?: string) =>
      setMessages(prev =>
        prev.map(m => {
          if (m.id !== assistantId) return m
          const segs = Array.isArray(m.content) ? m.content : []
          if (toolCallId) {
            const idx = segs.findIndex(s => s.kind === 'tool' && s.toolCallId === toolCallId)
            if (idx >= 0) {
              const updated = [...segs]
              updated[idx] = { kind: 'tool', text, toolCallId, toolStatus }
              return { ...m, content: updated }
            }
          }
          return { ...m, content: [...segs, { kind: 'tool', text, toolCallId, toolStatus }] }
        })
      )

    const finishStreaming = () =>
      setMessages(prev =>
        prev.map(m => (m.id === assistantId ? { ...m, isStreaming: false } : m))
      )

    try {
      const res = await api.run(agent, sessionId, prompt)
      await start(res, {
        onOut: (text) => appendSeg({ kind: 'text', text }),
        onStatus: (text) => appendSeg({ kind: 'status', text }),
        onTool: (text, toolCallId, toolStatus) => appendOrUpdateTool(text, toolCallId, toolStatus),
        onDone: () => finishStreaming(),
        onError: () => finishStreaming(),
      })
    } catch {
      finishStreaming()
    } finally {
      setIsRunning(false)
      refreshAll()
    }
  }, [agent, sessionId, isRunning, start, refreshAll])

  const setMode = useCallback(async (mode: string) => {
    await api.mode(agent, sessionId, mode)
    await loadState()
  }, [agent, sessionId, loadState])

  const setConfig = useCallback(async (key: string, value: string) => {
    await api.config(agent, sessionId, key, value)
    await loadState()
  }, [agent, sessionId, loadState])

  return {
    messages,
    images,
    sessionState,
    isRunning,
    send,
    cancel,
    setMode,
    setConfig,
    refreshAll,
    loadMessages,
    loadImages,
    loadState,
  }
}

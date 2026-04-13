import { useRef, useCallback } from 'react'
import type { SseEvent } from '../api/client'

type StreamHandlers = {
  onOut: (text: string, tag?: string) => void
  onStatus: (text: string, tag?: string) => void
  onTool: (text: string, toolCallId?: string, toolStatus?: string, tag?: string) => void
  onDone: (stopReason: string) => void
  onError: (message: string, code?: string) => void
}

/**
 * Manages a single SSE stream.
 * - Provides `start(response)` to begin consuming a fetch Response
 * - Provides `abort()` to cancel the current stream
 * - Handles heartbeat comments (": ping") transparently
 */
export function useStream() {
  const readerRef = useRef<ReadableStreamDefaultReader<Uint8Array> | null>(null)

  const abort = useCallback(() => {
    readerRef.current?.cancel()
    readerRef.current = null
  }, [])

  const start = useCallback(async (res: Response, handlers: StreamHandlers) => {
    if (!res.body) {
      handlers.onError('No response body')
      return
    }

    const reader = res.body.getReader()
    readerRef.current = reader
    const decoder = new TextDecoder()
    let buf = ''

    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buf += decoder.decode(value, { stream: true })
        const lines = buf.split('\n')
        buf = lines.pop() ?? ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          let ev: SseEvent
          try {
            ev = JSON.parse(line.slice(6)) as SseEvent
          } catch {
            continue
          }

          switch (ev.type) {
            case 'out':
              handlers.onOut(ev.data, ev.tag)
              break
            case 'status':
              handlers.onStatus(ev.data, ev.tag)
              break
            case 'tool':
              handlers.onTool(ev.data, ev.toolCallId, ev.toolStatus, ev.tag)
              break
            case 'done':
              handlers.onDone(ev.data)
              break
            case 'error':
              handlers.onError(ev.data, ev.code)
              break
          }
        }
      }
    } finally {
      readerRef.current = null
    }
  }, [])

  return { start, abort }
}

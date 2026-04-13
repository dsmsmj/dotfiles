import { useEffect, useRef, useState } from 'react'
import type { Message, Agent, Segment } from '../types'

type Props = {
  agent: Agent
  sessionId: string
  messages: Message[]
  isRunning: boolean
  availableCommands: string[]
  onSend: (prompt: string) => void
  onCancel: () => void
}

export default function ChatPanel({
  agent,
  sessionId,
  messages,
  isRunning,
  availableCommands,
  onSend,
  onCancel,
}: Props) {
  const [input, setInput] = useState('')
  const listRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight
    }
  }, [messages])

  const handleSend = () => {
    const text = input.trim()
    if (!text || isRunning) return
    onSend(text)
    setInput('')
    setTimeout(() => inputRef.current?.focus(), 0)
  }

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <span className="chat-title">对话</span>
        <span className="chat-meta">
          {agent} · <span className="chat-session-id">#{sessionId}</span>
        </span>
      </div>

      <div className="chat-messages" ref={listRef}>
        {messages.length === 0 ? (
          <div className="chat-empty">
            <div className="chat-empty-icon">✦</div>
            <p>向 <strong>{agent}</strong> 发送指令</p>
            <p className="chat-empty-hint">
              例如：基于 doc/进化学习法.md 创建海报
            </p>
          </div>
        ) : (
          messages.map(msg => <MessageBubble key={msg.id} message={msg} />)
        )}
      </div>

      {availableCommands.length > 0 && (
        <div className="cmd-bar">
          {availableCommands.map(cmd => (
            <button
              key={cmd}
              className="cmd-chip"
              disabled={isRunning}
              onClick={() => {
                setInput(cmd)
                inputRef.current?.focus()
              }}
            >
              {cmd}
            </button>
          ))}
        </div>
      )}

      <div className="chat-input-row">
        <textarea
          ref={inputRef}
          className="chat-input"
          placeholder={isRunning ? 'Agent 正在运行...' : '输入指令，Shift+Enter 换行，Enter 发送'}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              handleSend()
            }
          }}
          disabled={isRunning}
          rows={3}
        />
        <div className="chat-input-actions">
          {isRunning ? (
            <button className="btn-cancel" onClick={onCancel}>
              停止
            </button>
          ) : (
            <button
              className="btn-send"
              onClick={handleSend}
              disabled={!input.trim()}
            >
              发送
              <kbd>↵</kbd>
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === 'user'
  return (
    <div className={`message${isUser ? ' message-user' : ' message-ai'}`}>
      <div className="message-avatar" aria-label={isUser ? '用户' : 'AI'}>
        {isUser ? '你' : 'AI'}
      </div>
      <div className="message-body">
        {typeof message.content === 'string'
          ? <pre className="message-text">{message.content}</pre>
          : <AssistantContent segments={message.content} isStreaming={message.isStreaming} />
        }
      </div>
    </div>
  )
}

function AssistantContent({ segments, isStreaming }: { segments: Segment[]; isStreaming?: boolean }) {
  return (
    <div className="message-segments">
      {segments.map((seg, i) => {
        if (seg.kind === 'text') {
          return <pre key={i} className="message-text">{seg.text}</pre>
        }
        if (seg.kind === 'status') {
          return <div key={i} className="message-status">{seg.text}</div>
        }
        if (seg.kind === 'tool') {
          return (
            <div key={seg.toolCallId ?? i} className={`message-tool${seg.toolStatus ? ` tool-${seg.toolStatus}` : ''}`}>
              {seg.text}
              {seg.toolStatus && <span className="tool-status-badge">{seg.toolStatus}</span>}
            </div>
          )
        }
        return null
      })}
      {isStreaming && <span className="message-cursor" aria-hidden />}
    </div>
  )
}

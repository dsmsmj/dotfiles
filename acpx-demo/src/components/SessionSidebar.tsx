import { useState, useRef, useEffect } from 'react'

type Props = {
  sessionId: string
  sessions: string[]
  isRunning: boolean
  onSessionChange: (sessionId: string) => void
  onNewSession: (sessionId: string) => void
}

export default function SessionSidebar({
  sessionId,
  sessions,
  isRunning,
  onSessionChange,
  onNewSession,
}: Props) {
  const [showNew, setShowNew] = useState(false)
  const [newId, setNewId] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (showNew) inputRef.current?.focus()
  }, [showNew])

  const commit = () => {
    const id = newId.trim()
    if (id) onNewSession(id)
    setNewId('')
    setShowNew(false)
  }

  const allSessions = sessions.includes(sessionId)
    ? sessions
    : [sessionId, ...sessions]

  return (
    <aside className="session-sidebar">
      <div className="session-sidebar-header">
        <span className="session-sidebar-title">Sessions</span>
        <button
          className="btn-icon"
          onClick={() => setShowNew(v => !v)}
          disabled={isRunning}
          title="新建 Session"
        >
          +
        </button>
      </div>

      {showNew && (
        <div className="session-sidebar-new">
          <input
            ref={inputRef}
            className="new-session-input"
            placeholder="Session ID"
            value={newId}
            onChange={e => setNewId(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter') commit()
              if (e.key === 'Escape') { setNewId(''); setShowNew(false) }
            }}
          />
          <button className="btn-icon" onClick={commit}>✓</button>
          <button className="btn-icon" onClick={() => setShowNew(false)}>✕</button>
        </div>
      )}

      <ul className="session-sidebar-list">
        {allSessions.map(s => (
          <li key={s}>
            <button
              className={`session-sidebar-item${s === sessionId ? ' active' : ''}`}
              onClick={() => onSessionChange(s)}
              disabled={isRunning && s !== sessionId}
              title={s}
            >
              {s}
            </button>
          </li>
        ))}
      </ul>
    </aside>
  )
}

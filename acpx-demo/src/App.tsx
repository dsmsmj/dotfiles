import { useState, useEffect, useCallback } from 'react'
import SessionBar from './components/SessionBar'
import SessionSidebar from './components/SessionSidebar'
import ChatPanel from './components/ChatPanel'
import ImageGallery from './components/ImageGallery'
import { useSession } from './hooks/useSession'
import { api } from './api/client'
import type { Agent } from './types'
import './App.css'

export default function App() {
  const [agent, setAgent] = useState<Agent>('qwen')
  const [sessionId, setSessionId] = useState('q01')
  const [sessions, setSessions] = useState<string[]>([])

  const {
    messages,
    images,
    sessionState,
    isRunning,
    send,
    cancel,
    refreshAll,
    loadMessages,
    loadImages,
    loadState,
  } = useSession(agent, sessionId)

  const loadSessions = useCallback(async () => {
    try {
      const { sessions: list } = await api.sessions.list(agent)
      setSessions(list)
    } catch { /* network not ready */ }
  }, [agent])

  useEffect(() => { void loadSessions() }, [loadSessions])
  useEffect(() => { void loadMessages() }, [loadMessages])
  useEffect(() => { void loadImages() }, [loadImages])
  useEffect(() => { void loadState() }, [loadState])

  const handleAgentChange = useCallback((newAgent: Agent) => {
    setAgent(newAgent)
    setSessionId('')
    setSessions([])
  }, [])

  const handleSessionChange = useCallback((id: string) => {
    setSessionId(id)
  }, [])

  const handleNewSession = useCallback((id: string) => {
    setSessions(prev => (prev.includes(id) ? prev : [...prev, id]))
    setSessionId(id)
  }, [])

  const handleSend = useCallback(async (prompt: string) => {
    await send(prompt)
    await loadSessions()
  }, [send, loadSessions])

  return (
    <div className="app">
      <SessionBar
        agent={agent}
        sessionId={sessionId}
        isRunning={isRunning}
        currentMode={sessionState.currentMode}
        onAgentChange={handleAgentChange}
      />
      <div className="body">
        <SessionSidebar
          sessionId={sessionId}
          sessions={sessions}
          isRunning={isRunning}
          onSessionChange={handleSessionChange}
          onNewSession={handleNewSession}
        />
        <div className="main">
          <ChatPanel
            agent={agent}
            sessionId={sessionId}
            messages={messages}
            isRunning={isRunning}
            availableCommands={sessionState.availableCommands}
            onSend={handleSend}
            onCancel={cancel}
          />
          <ImageGallery
            sessionId={sessionId}
            images={images}
            onRefresh={refreshAll}
          />
        </div>
      </div>
    </div>
  )
}

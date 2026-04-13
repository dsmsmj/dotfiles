import type { Agent } from '../types'
import { AGENTS } from '../types'

type Props = {
  agent: Agent
  sessionId: string
  isRunning: boolean
  currentMode: string | null
  onAgentChange: (agent: Agent) => void
}

export default function SessionBar({
  agent,
  sessionId,
  isRunning,
  currentMode,
  onAgentChange,
}: Props) {
  return (
    <header className="session-bar">
      <span className="session-bar-logo">ACPX Studio</span>

      <div className="session-bar-controls">
        <label className="ctrl-group">
          <span className="ctrl-label">Agent</span>
          <select
            className="ctrl-select"
            value={agent}
            onChange={e => onAgentChange(e.target.value as Agent)}
            disabled={isRunning}
          >
            {AGENTS.map(a => <option key={a} value={a}>{a}</option>)}
          </select>
        </label>

        <span className="ctrl-sep" />

        <span className="ctrl-label session-id-display" title={sessionId}>{sessionId}</span>

        {currentMode && (
          <>
            <span className="ctrl-sep" />
            <span className="ctrl-badge">{currentMode}</span>
          </>
        )}
      </div>

      <div className="session-bar-right">
        {isRunning && (
          <span className="status-running">
            <span className="status-dot" />
            Running
          </span>
        )}
      </div>
    </header>
  )
}

import { useState, useEffect, useCallback } from 'react';
import AgentTaskLog from '../components/AgentTaskLog';
import './FleetDashboard.css';

const POLL_INTERVAL = 3000;

const AGENT_META = {
  'Gemini Antigravity': { icon: '♊', color: '#a78bfa' },
  'Claude Design':      { icon: '✦', color: '#f472b6' },
  'Claude Code':        { icon: '⌨',  color: '#00d4a8' },
  'Hermes':             { icon: '⚡', color: '#f5a623' },
  'Ollama':             { icon: '🦙', color: '#60a5fa' },
};

const MOCK_AGENTS = [
  { id: 1, name: 'Gemini Antigravity', role: 'Backend Architect',    status: 'working', task: 'Designing fleet_status endpoint schema' },
  { id: 2, name: 'Claude Design',      role: 'UI/UX Designer',       status: 'working', task: 'Rendering FleetDashboard glassmorphism layout' },
  { id: 3, name: 'Claude Code',        role: 'Full-Stack Engineer',  status: 'idle',    task: null },
  { id: 4, name: 'Hermes',             role: 'Comms & Relay',        status: 'idle',    task: null },
  { id: 5, name: 'Ollama',             role: 'Local LLM Runner',     status: 'offline', task: null },
];

function statusCounts(agents) {
  return agents.reduce(
    (acc, a) => { acc[a.status] = (acc[a.status] || 0) + 1; return acc; },
    { working: 0, idle: 0, offline: 0 },
  );
}

function AgentCard({ agent }) {
  const meta = AGENT_META[agent.name] || { icon: '◈', color: '#e8f0fe' };
  return (
    <div className={`fd-agent-card status-${agent.status}`}>
      <div className="fd-card-glow" style={{ '--agent-color': meta.color }} />

      <div className="fd-card-header">
        <div className="fd-agent-icon" style={{ '--agent-color': meta.color }}>
          {meta.icon}
        </div>
        <div className={`fd-status-pip status-pip-${agent.status}`} />
      </div>

      <div className="fd-agent-name">{agent.name}</div>
      <div className="fd-agent-role">{agent.role}</div>

      <div className={`fd-status-badge badge-${agent.status}`}>
        <span className={`fd-status-dot dot-${agent.status}`} />
        {agent.status.toUpperCase()}
      </div>

      {agent.task && (
        <div className="fd-agent-task">
          <span className="fd-task-label">TASK</span>
          <span className="fd-task-text">{agent.task}</span>
        </div>
      )}
    </div>
  );
}

export default function FleetDashboard() {
  const [agents, setAgents] = useState(MOCK_AGENTS);
  const [error, setError]   = useState(null);
  const [lastPoll, setLastPoll] = useState(null);
  const [pulse, setPulse]   = useState(false);

  const poll = useCallback(async () => {
    try {
      const res = await fetch('http://localhost:5000/api/fleet_status');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setAgents(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLastPoll(new Date().toLocaleTimeString('en-GB', { hour12: false }));
      setPulse(true);
      setTimeout(() => setPulse(false), 400);
    }
  }, []);

  useEffect(() => {
    poll();
    const id = setInterval(poll, POLL_INTERVAL);
    return () => clearInterval(id);
  }, [poll]);

  const counts = statusCounts(agents);

  return (
    <div className="fd-root">
      {/* ambient background orbs */}
      <div className="fd-orb fd-orb-1" />
      <div className="fd-orb fd-orb-2" />
      <div className="fd-orb fd-orb-3" />

      {/* ── Top Bar ───────────────────────────── */}
      <header className="fd-topbar">
        <div className="fd-topbar-left">
          <div className="fd-logo-mark">
            <span className="fd-logo-icon">⬡</span>
            <div>
              <div className="fd-logo-title">Fleet AI Orchestration</div>
              <div className="fd-logo-sub">ProCare Intelligence · Multi-Agent Control</div>
            </div>
          </div>
        </div>

        <div className="fd-topbar-center">
          <div className="fd-stat-pill working">
            <span className="fd-stat-dot dot-working" />
            <span className="fd-stat-num">{counts.working}</span>
            <span className="fd-stat-lbl">Working</span>
          </div>
          <div className="fd-stat-pill idle">
            <span className="fd-stat-dot dot-idle" />
            <span className="fd-stat-num">{counts.idle}</span>
            <span className="fd-stat-lbl">Idle</span>
          </div>
          <div className="fd-stat-pill offline">
            <span className="fd-stat-dot dot-offline" />
            <span className="fd-stat-num">{counts.offline}</span>
            <span className="fd-stat-lbl">Offline</span>
          </div>
        </div>

        <div className="fd-topbar-right">
          {error && <div className="fd-error-badge">⚠ {error}</div>}
          <div className={`fd-live-badge ${pulse ? 'fd-pulse-flash' : ''}`}>
            <span className="fd-live-dot" />
            LIVE · {lastPoll || '––:––:––'}
          </div>
        </div>
      </header>

      {/* ── Main Grid ─────────────────────────── */}
      <main className="fd-main">

        {/* Agent Cards Grid */}
        <section className="fd-section">
          <div className="fd-section-label">
            <span className="fd-section-line" />
            ACTIVE AGENTS
            <span className="fd-section-count">{agents.length}</span>
            <span className="fd-section-line" />
          </div>
          <div className="fd-agent-grid">
            {agents.map((agent) => (
              <AgentCard key={agent.id} agent={agent} />
            ))}
          </div>
        </section>

        {/* Task Log Terminal */}
        <section className="fd-log-section">
          <div className="fd-section-label">
            <span className="fd-section-line" />
            TASK LOG
            <span className="fd-section-line" />
          </div>
          <AgentTaskLog agents={agents} />
        </section>

      </main>
    </div>
  );
}

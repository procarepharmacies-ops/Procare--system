import { useEffect, useRef } from 'react';
import './AgentTaskLog.css';

const STATUS_SYMBOL = { working: '▶', idle: '◉', offline: '✕' };

export default function AgentTaskLog({ agents }) {
  const bottomRef = useRef(null);
  const now = new Date().toLocaleTimeString('en-GB', { hour12: false });

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [agents]);

  const lines = agents.flatMap((agent) => [
    {
      id: `${agent.id}-sep`,
      type: 'separator',
      text: `── ${agent.name} ──────────────────────────`,
    },
    {
      id: `${agent.id}-status`,
      type: agent.status,
      text: `[${now}] ${STATUS_SYMBOL[agent.status] || '?'} STATUS: ${agent.status.toUpperCase()} — ${agent.role}`,
    },
    ...(agent.task
      ? [{ id: `${agent.id}-task`, type: 'task', text: `           TASK › ${agent.task}` }]
      : []),
  ]);

  return (
    <div className="atl-shell">
      <div className="atl-titlebar">
        <span className="atl-traffic red" />
        <span className="atl-traffic yellow" />
        <span className="atl-traffic green" />
        <span className="atl-title">fleet_orchestrator — agent_task_log</span>
        <span className="atl-badge">LIVE</span>
      </div>
      <div className="atl-body">
        <p className="atl-line separator">
          {'═'.repeat(60)} FLEET TASK LOG {'═'.repeat(4)}
        </p>
        {lines.map((line) => (
          <p key={line.id} className={`atl-line ${line.type}`}>
            {line.text}
          </p>
        ))}
        {agents.length === 0 && (
          <p className="atl-line separator">Awaiting agent telemetry…</p>
        )}
        <div ref={bottomRef} />
        <span className="atl-cursor">█</span>
      </div>
    </div>
  );
}

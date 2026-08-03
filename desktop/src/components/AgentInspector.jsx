/**
 * Right Agent & Memory Inspector Component for Astra OS Desktop Shell.
 */

export function AgentInspector({ activeAgents, memoryStats, logs }) {
  return (
    <div className="agent-inspector">
      <h3 style={{ color: '#38bdf8', marginTop: 0 }}>🔍 Agent Inspector</h3>

      <div style={{ marginBottom: '20px' }}>
        <h4>Active Agents ({activeAgents.length})</h4>
        {activeAgents.length === 0 ? (
          <div style={{ color: '#64748b', fontSize: '0.9rem' }}>No agents running.</div>
        ) : (
          activeAgents.map((ag, i) => (
            <div key={i} style={{ background: '#0f172a', padding: '8px 12px', borderRadius: '6px', marginBottom: '8px', fontSize: '0.85rem' }}>
              <strong>{ag.name}</strong> <span className="badge badge-active">{ag.status}</span>
            </div>
          ))
        )}
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h4>Memory Stats</h4>
        <div style={{ fontSize: '0.85rem', color: '#cbd5e1' }}>
          <div>Episodic Records: {memoryStats.episodic_count || 0}</div>
          <div>Semantic Embeddings: {memoryStats.semantic_count || 0}</div>
          <div>Working Memory Buffer: {memoryStats.buffer_size || 0} msgs</div>
        </div>
      </div>

      <div>
        <h4>Recent Logs</h4>
        <div style={{ background: '#020617', padding: '10px', borderRadius: '6px', height: '180px', overflowY: 'auto', fontSize: '0.75rem', color: '#a7f3d0' }}>
          {logs.slice(-10).map((l, i) => (
            <div key={i}>[{l.level}] {l.message}</div>
          ))}
        </div>
      </div>
    </div>
  );
}

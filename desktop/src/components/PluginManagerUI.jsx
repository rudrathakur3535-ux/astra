/**
 * Plugin Manager View Component for Astra OS Desktop Shell.
 */

export function PluginManagerUI({ plugins, onTogglePlugin }) {
  return (
    <div style={{ padding: '20px', height: '100%', overflowY: 'auto' }}>
      <h2 style={{ color: '#38bdf8' }}>🔌 Plugin Platform Manager</h2>
      <p style={{ color: '#94a3b8' }}>Installed plugins and permissions configuration.</p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '20px', marginTop: '20px' }}>
        {plugins.map(p => (
          <div key={p.id} style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '8px', padding: '15px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0 }}>{p.name}</h3>
              <span className={`badge ${p.enabled ? 'badge-healthy' : ''}`}>{p.enabled ? 'Enabled' : 'Disabled'}</span>
            </div>
            <p style={{ fontSize: '0.85rem', color: '#94a3b8', margin: '10px 0' }}>{p.description}</p>
            <div style={{ fontSize: '0.75rem', color: '#cbd5e1' }}>Version: {p.version}</div>
            <button
              onClick={() => onTogglePlugin(p.id)}
              style={{
                marginTop: '15px',
                width: '100%',
                background: p.enabled ? '#334155' : '#0284c7',
                color: '#fff',
                border: 'none',
                padding: '8px',
                borderRadius: '6px',
                cursor: 'pointer'
              }}
            >
              {p.enabled ? 'Disable Plugin' : 'Enable Plugin'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

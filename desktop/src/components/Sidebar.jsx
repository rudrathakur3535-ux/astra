/**
 * Sidebar Navigation Component for Astra OS Desktop Shell.
 */

export function Sidebar({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'chat', label: '💬 Conversation', icon: '💬' },
    { id: 'projects', label: '📂 Projects', icon: '📂' },
    { id: 'knowledge', label: '🧠 Knowledge', icon: '🧠' },
    { id: 'plugins', label: '🔌 Plugins', icon: '🔌' },
    { id: 'settings', label: '⚙️ Settings', icon: '⚙️' }
  ];

  return (
    <div className="sidebar">
      <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#38bdf8', marginBottom: '20px' }}>
        🚀 Astra OS
      </div>
      {navItems.map(item => (
        <div
          key={item.id}
          className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
          onClick={() => setActiveTab(item.id)}
        >
          <span>{item.icon}</span>
          <span>{item.label}</span>
        </div>
      ))}
      <div style={{ marginTop: 'auto', fontSize: '0.8rem', color: '#64748b' }}>
        v1.0.0-desktop (Connected)
      </div>
    </div>
  );
}

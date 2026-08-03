/**
 * Main Application Shell Component for Astra OS Desktop (React).
 */

import { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { ChatCanvas } from './components/ChatCanvas';
import { AgentInspector } from './components/AgentInspector';
import { VoiceControlBar } from './components/VoiceControlBar';
import { PluginManagerUI } from './components/PluginManagerUI';
import { SettingsUI } from './components/SettingsUI';

export default function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [messages, setMessages] = useState([
    { sender: 'assistant', text: 'Hello! I am Astra OS. How can I assist your desktop or coding environment today?' }
  ]);
  const [isExecuting, setIsExecuting] = useState(false);
  const [activeAgents, setActiveAgents] = useState([]);
  const [memoryStats, setMemoryStats] = useState({ episodic_count: 14, semantic_count: 128, buffer_size: 4 });
  const [logs, setLogs] = useState([
    { level: 'INFO', message: 'Astra Desktop Runtime bridge initialized.' },
    { level: 'INFO', message: 'Connected to FastAPI backend.' }
  ]);
  const [voiceStatus, setVoiceStatus] = useState({
    is_listening: false,
    stt_engine: 'Whisper',
    tts_engine: 'ElevenLabs',
    wakeword_active: true,
    health: 'healthy'
  });
  const [plugins, setPlugins] = useState([
    { id: 'web-search', name: 'Web Search Tool', description: 'Search & scrape web resources via Playwright', enabled: true, version: '1.2.0' },
    { id: 'code-analyzer', name: 'Code Intelligence', description: 'AST parsing & dependency graph extraction', enabled: true, version: '1.0.0' }
  ]);
  const [settings, setSettings] = useState({
    llm_provider: 'openai',
    voice_engine: 'elevenlabs',
    wake_word: 'Hey Astra',
    theme: 'dark'
  });

  const handleSendMessage = (text) => {
    setMessages(prev => [...prev, { sender: 'user', text }]);
    setIsExecuting(true);

    // Mock agent workflow response
    setTimeout(() => {
      setMessages(prev => [...prev, {
        sender: 'assistant',
        text: `Executed workflow for request: "${text}". Multi-agent execution completed in 240ms.`
      }]);
      setIsExecuting(false);
    }, 1000);
  };

  return (
    <div className="desktop-container">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {activeTab === 'chat' && (
        <>
          <ChatCanvas messages={messages} onSendMessage={handleSendMessage} isExecuting={isExecuting} />
          <AgentInspector activeAgents={activeAgents} memoryStats={memoryStats} logs={logs} />
        </>
      )}

      {activeTab === 'plugins' && (
        <PluginManagerUI plugins={plugins} onTogglePlugin={(id) => {
          setPlugins(prev => prev.map(p => p.id === id ? { ...p, enabled: !p.enabled } : p));
        }} />
      )}

      {activeTab === 'settings' && (
        <SettingsUI settings={settings} onUpdateSettings={(newSettings) => {
          setSettings(newSettings);
          alert('Configuration updated!');
        }} />
      )}

      {activeTab !== 'chat' && activeTab !== 'plugins' && activeTab !== 'settings' && (
        <div style={{ padding: '40px', color: '#94a3b8' }}>
          <h2>{activeTab.toUpperCase()} Module View</h2>
          <p>Workplace component under execution.</p>
        </div>
      )}

      <VoiceControlBar
        voiceStatus={voiceStatus}
        onToggleWakeWord={() => setVoiceStatus(prev => ({ ...prev, wakeword_active: !prev.wakeword_active }))}
        onToggleMic={() => setVoiceStatus(prev => ({ ...prev, is_listening: !prev.is_listening }))}
      />
    </div>
  );
}

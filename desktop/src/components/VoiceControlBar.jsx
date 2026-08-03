/**
 * Bottom Voice Control Bar Component for Astra OS Desktop Shell.
 */

export function VoiceControlBar({ voiceStatus, onToggleWakeWord, onToggleMic }) {
  return (
    <div className="voice-control-bar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
        <button
          onClick={onToggleMic}
          style={{
            background: voiceStatus.is_listening ? '#ef4444' : '#1e293b',
            color: '#fff',
            border: '1px solid #334155',
            padding: '8px 15px',
            borderRadius: '20px',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          🎙 {voiceStatus.is_listening ? 'Listening...' : 'Mic Off'}
        </button>
        <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
          STT: {voiceStatus.stt_engine} | TTS: {voiceStatus.tts_engine}
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
        <label style={{ fontSize: '0.85rem', color: '#cbd5e1', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <input
            type="checkbox"
            checked={voiceStatus.wakeword_active}
            onChange={onToggleWakeWord}
          />
          Wake Word ("Hey Astra")
        </label>
        <span className={`badge ${voiceStatus.health === 'healthy' ? 'badge-healthy' : 'badge-active'}`}>
          {voiceStatus.health.toUpperCase()}
        </span>
      </div>
    </div>
  );
}

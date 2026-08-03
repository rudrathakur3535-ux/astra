/**
 * Settings UI Component for Astra OS Desktop Shell.
 */

export function SettingsUI({ settings, onUpdateSettings }) {
  return (
    <div style={{ padding: '20px', height: '100%', overflowY: 'auto' }}>
      <h2 style={{ color: '#38bdf8' }}>⚙️ Astra System Settings</h2>
      <p style={{ color: '#94a3b8' }}>Configure AI providers, voice engines, and runtime parameters.</p>

      <form onSubmit={(e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        onUpdateSettings({
          llm_provider: formData.get('llm_provider'),
          voice_engine: formData.get('voice_engine'),
          wake_word: formData.get('wake_word'),
          theme: formData.get('theme')
        });
      }} style={{ maxWidth: '500px', display: 'flex', flexDirection: 'column', gap: '20px', marginTop: '20px' }}>

        <div>
          <label style={{ display: 'block', marginBottom: '8px', color: '#cbd5e1' }}>AI LLM Provider</label>
          <select name="llm_provider" defaultValue={settings.llm_provider} style={{ width: '100%', background: '#1e293b', color: '#fff', border: '1px solid #334155', padding: '10px', borderRadius: '6px' }}>
            <option value="openai">OpenAI (GPT-4o)</option>
            <option value="gemini">Google Gemini (Gemini 1.5 Pro)</option>
            <option value="anthropic">Anthropic (Claude 3.5 Sonnet)</option>
            <option value="local">Local Ollama / Llama 3</option>
          </select>
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '8px', color: '#cbd5e1' }}>Voice TTS Engine</label>
          <select name="voice_engine" defaultValue={settings.voice_engine} style={{ width: '100%', background: '#1e293b', color: '#fff', border: '1px solid #334155', padding: '10px', borderRadius: '6px' }}>
            <option value="elevenlabs">ElevenLabs (Expressive Female)</option>
            <option value="pyttsx3">PyTTSx3 (Local System Voice)</option>
          </select>
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '8px', color: '#cbd5e1' }}>Wake Word Phrase</label>
          <input type="text" name="wake_word" defaultValue={settings.wake_word} style={{ width: '100%', background: '#1e293b', color: '#fff', border: '1px solid #334155', padding: '10px', borderRadius: '6px' }} />
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '8px', color: '#cbd5e1' }}>UI Theme</label>
          <select name="theme" defaultValue={settings.theme} style={{ width: '100%', background: '#1e293b', color: '#fff', border: '1px solid #334155', padding: '10px', borderRadius: '6px' }}>
            <option value="dark">Dark Glassmorphism</option>
            <option value="cyberpunk">Cyberpunk Neon</option>
          </select>
        </div>

        <button type="submit" style={{ background: '#38bdf8', color: '#0f172a', border: 'none', padding: '12px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer' }}>
          Save Configuration
        </button>
      </form>
    </div>
  );
}

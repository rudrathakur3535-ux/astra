/**
 * Center Chat Canvas Component for Astra OS Desktop Shell.
 */

export function ChatCanvas({ messages, onSendMessage, isExecuting }) {
  return (
    <div className="chat-canvas">
      <div style={{ padding: '15px 20px', borderBottom: '1px solid #334155', fontWeight: 'bold' }}>
        Astra Intelligence Canvas
      </div>
      <div style={{ flex: 1, padding: '20px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '15px' }}>
        {messages.length === 0 ? (
          <div style={{ margin: 'auto', color: '#64748b', textAlign: 'center' }}>
            <h2>Ask Astra anything...</h2>
            <p>Voice command or prompt multi-agent workflows.</p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} style={{
              alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
              background: msg.sender === 'user' ? '#0284c7' : '#1e293b',
              color: '#f8fafc',
              padding: '12px 18px',
              borderRadius: '12px',
              maxWidth: '70%'
            }}>
              <strong>{msg.sender === 'user' ? 'You' : 'Astra OS'}:</strong>
              <div style={{ marginTop: '5px' }}>{msg.text}</div>
            </div>
          ))
        )}
      </div>
      <form onSubmit={(e) => {
        e.preventDefault();
        const input = e.target.elements.prompt;
        if (input.value.trim()) {
          onSendMessage(input.value);
          input.value = '';
        }
      }} style={{ padding: '15px', borderTop: '1px solid #334155', display: 'flex', gap: '10px' }}>
        <input
          name="prompt"
          type="text"
          placeholder="Type your prompt or request..."
          disabled={isExecuting}
          style={{
            flex: 1,
            background: '#1e293b',
            border: '1px solid #334155',
            color: '#f8fafc',
            padding: '12px 15px',
            borderRadius: '8px',
            outline: 'none'
          }}
        />
        <button
          type="submit"
          disabled={isExecuting}
          style={{
            background: '#38bdf8',
            color: '#0f172a',
            border: 'none',
            padding: '0 20px',
            borderRadius: '8px',
            fontWeight: 'bold',
            cursor: 'pointer'
          }}
        >
          {isExecuting ? 'Running...' : 'Send'}
        </button>
      </form>
    </div>
  );
}

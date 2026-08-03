"""
FastAPI Dashboard API & Real-Time WebSocket Router for Project Astra OS.
Provides REST and WebSocket endpoints for live observability metrics, tracing, health, and developer dashboard.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, List, Dict, Any
import asyncio
import json

from app.observability.dashboard_service import DashboardService
from app.models.health_status import HealthState

router = APIRouter(tags=["observability"])

# Shared global dashboard service instance for API injection
_dashboard_service_instance: Optional[DashboardService] = None


def get_dashboard_service() -> DashboardService:
    """Returns or initializes the global DashboardService instance."""
    global _dashboard_service_instance
    if _dashboard_service_instance is None:
        _dashboard_service_instance = DashboardService()
    return _dashboard_service_instance


def set_dashboard_service(service: DashboardService) -> None:
    """Sets the global DashboardService instance."""
    global _dashboard_service_instance
    _dashboard_service_instance = service


@router.get("/dashboard/summary", response_class=JSONResponse)
async def get_summary():
    """
    Returns full dashboard summary payload.
    """
    service = get_dashboard_service()
    return service.get_dashboard_summary()


@router.get("/metrics", response_class=JSONResponse)
async def get_metrics():
    """
    Returns detailed metrics breakdown.
    """
    service = get_dashboard_service()
    return service.metrics_service.get_summary()


@router.get("/traces/{trace_id}", response_class=JSONResponse)
async def get_trace(trace_id: str):
    """
    Returns all spans for a specific Trace ID.
    """
    service = get_dashboard_service()
    spans = service.trace_manager.get_trace_spans(trace_id)
    if not spans:
        raise HTTPException(status_code=404, detail=f"Trace ID '{trace_id}' not found.")
    return [span.to_dict() for span in spans]


@router.get("/health", response_class=JSONResponse)
async def get_health():
    """
    Returns subsystem health report.
    """
    service = get_dashboard_service()
    return service.health_monitor.check_all()


@router.get("/logs", response_class=JSONResponse)
async def get_logs(
    level: Optional[str] = Query(None, description="Filter log level: INFO, WARNING, ERROR, DEBUG"),
    subsystem: Optional[str] = Query(None, description="Filter subsystem name"),
    trace_id: Optional[str] = Query(None, description="Filter by Trace ID"),
    search: Optional[str] = Query(None, description="Keyword search query"),
    limit: int = Query(50, ge=1, le=500)
):
    """
    Returns filtered log records.
    """
    service = get_dashboard_service()
    return service.log_aggregator.query(
        level=level,
        subsystem=subsystem,
        trace_id=trace_id,
        search_query=search,
        limit=limit
    )


@router.get("/timeline", response_class=JSONResponse)
async def get_timeline(trace_id: Optional[str] = None, limit: int = Query(50, ge=1, le=200)):
    """
    Returns chronological workflow timeline.
    """
    service = get_dashboard_service()
    if trace_id:
        return service.event_timeline.get_timeline_for_trace(trace_id)
    return service.event_timeline.get_recent_events(limit=limit)


@router.get("/workflow-graph", response_class=JSONResponse)
async def get_workflow_graph(trace_id: Optional[str] = None):
    """
    Returns workflow DAG node-and-edge visualization graph.
    """
    service = get_dashboard_service()
    if trace_id:
        spans = service.trace_manager.get_trace_spans(trace_id)
        return service.workflow_visualizer.generate_workflow_dag(spans)
    return service.workflow_visualizer.generate_live_agent_graph([])


@router.get("/profiler/recommendations", response_class=JSONResponse)
async def get_profiler_recommendations():
    """
    Returns latency percentiles (P50, P95, P99) and automated optimization recommendations.
    """
    service = get_dashboard_service()
    return service.performance_profiler.get_profiler_stats()


@router.get("/dashboard", response_class=HTMLResponse)
async def render_dashboard():
    """
    Renders an embedded HTML Developer & Interactive Voice Command Dashboard UI.
    """
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ASTRA OS — Intelligent Voice & Developer Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; }
        body { font-family: 'Inter', 'Segoe UI', sans-serif; background: #0b0f19; color: #f8fafc; margin: 0; padding: 24px; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 18px; margin-bottom: 24px; }
        .header h1 { margin: 0; font-size: 1.8rem; color: #38bdf8; background: linear-gradient(135deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 15px; margin-bottom: 25px; }
        .card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
        .card h3 { margin-top: 0; color: #94a3b8; font-size: 0.85em; text-transform: uppercase; letter-spacing: 0.5px; }
        .card .value { font-size: 1.8em; font-weight: bold; color: #38bdf8; margin: 8px 0; }
        .status-healthy { color: #4ade80; }
        .status-degraded { color: #facc15; }
        .status-unhealthy { color: #f87171; }

        /* Voice Console Styles */
        .voice-section {
            background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid #334155;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 28px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        }
        .voice-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
        .voice-header h2 { margin: 0; font-size: 1.25rem; color: #38bdf8; display: flex; align-items: center; gap: 10px; }
        .mic-btn-container { display: flex; flex-direction: column; align-items: center; margin: 15px 0 20px 0; }
        .mic-btn {
            background: linear-gradient(135deg, #0284c7, #2563eb);
            color: #ffffff;
            border: none;
            width: 85px;
            height: 85px;
            border-radius: 50%;
            font-size: 2.2rem;
            cursor: pointer;
            outline: none;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 0 25px rgba(2, 132, 199, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .mic-btn:hover { transform: scale(1.08); box-shadow: 0 0 35px rgba(56, 189, 248, 0.7); }
        .mic-btn.listening {
            background: linear-gradient(135deg, #dc2626, #ef4444);
            animation: pulse 1.4s infinite;
            box-shadow: 0 0 40px rgba(239, 68, 68, 0.8);
        }
        @keyframes pulse {
            0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
            70% { transform: scale(1.1); box-shadow: 0 0 0 20px rgba(239, 68, 68, 0); }
            100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
        }
        .mic-status-label { margin-top: 10px; font-size: 0.95rem; font-weight: 600; color: #94a3b8; }
        .prompt-form { display: flex; gap: 12px; margin-top: 15px; }
        .prompt-input { flex: 1; background: #0f172a; border: 1px solid #334155; border-radius: 10px; padding: 12px 16px; color: #f8fafc; font-size: 1rem; outline: none; }
        .prompt-input:focus { border-color: #38bdf8; box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2); }
        .exec-btn { background: #38bdf8; color: #0f172a; border: none; border-radius: 10px; padding: 0 22px; font-weight: 700; font-size: 1rem; cursor: pointer; transition: background 0.2s; }
        .exec-btn:hover { background: #7dd3fc; }
        .presets { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 14px; }
        .preset-chip { background: #1e293b; border: 1px solid #334155; color: #cbd5e1; padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; cursor: pointer; transition: all 0.2s; }
        .preset-chip:hover { background: #334155; color: #38bdf8; border-color: #38bdf8; }
        .response-box { margin-top: 20px; background: #0f172a; border: 1px solid #334155; border-radius: 12px; padding: 18px; display: none; }
        .audio-toggle { display: flex; align-items: center; gap: 8px; color: #cbd5e1; font-size: 0.9rem; cursor: pointer; }

        table { width: 100%; border-collapse: collapse; background: #1e293b; margin-top: 15px; border-radius: 8px; overflow: hidden; border: 1px solid #334155; }
        th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #334155; }
        th { background: #0f172a; color: #38bdf8; font-weight: 600; }
        pre { background: #0f172a; padding: 14px; border-radius: 8px; overflow-x: auto; color: #a7f3d0; border: 1px solid #334155; max-height: 250px; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>🚀 ASTRA OS — Observability & Companion Dashboard</h1>
            <span style="color:#94a3b8; font-size:0.85rem;">Personal AI Operating System Control Center</span>
        </div>
        <div style="display:flex; gap:12px;">
            <a href="/avatar/view" target="_blank" style="color:#38bdf8; text-decoration:none; font-weight:600; font-size:0.9rem; background:#1e293b; padding:6px 14px; border-radius:20px; border:1px solid #334155;">Full Avatar Studio ↗</a>
            <a href="/docs" target="_blank" style="color:#38bdf8; text-decoration:none; font-weight:600; font-size:0.9rem; background:#1e293b; padding:6px 14px; border-radius:20px; border:1px solid #334155;">FastAPI Swagger Docs ↗</a>
        </div>
    </div>

    <!-- Main Companion & Voice Grid -->
    <div style="display:flex; gap:20px; margin-bottom:28px; flex-wrap:wrap;">
        <!-- Astra 2D Animated Character Widget -->
        <div style="flex:0 0 380px; background:linear-gradient(180deg, #1e293b 0%, #0f172a 100%); border:1px solid #334155; border-radius:16px; padding:16px; display:flex; flex-direction:column; align-items:center; box-shadow:0 10px 30px rgba(0,0,0,0.4);">
            <div style="width:100%; display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <span style="font-weight:700; color:#38bdf8; font-size:1.05rem;">✨ Astra AI Companion</span>
                <span id="avatarEmotionTag" style="font-size:0.75rem; font-weight:700; color:#4ade80; background:rgba(74,222,128,0.15); padding:2px 8px; border-radius:12px; border:1px solid rgba(74,222,128,0.3);">LIVE</span>
            </div>
            <div id="dash-avatar-container" style="width:340px; height:580px;"></div>
        </div>

        <!-- Voice Command & Agent Console -->
        <div class="voice-section" style="flex:1; margin-bottom:0;">
            <div class="voice-header">
                <h2>🎙 Interactive Voice Command Console</h2>
                <label class="audio-toggle">
                    <input type="checkbox" id="ttsToggle" checked> 🔊 Speak Response Out Loud (TTS)
                </label>
            </div>

            <div class="mic-btn-container">
                <button id="micBtn" class="mic-btn" onclick="toggleVoiceInput()" title="Click to Speak Voice Command">
                    🎙
                </button>
                <div id="micStatus" class="mic-status-label">Click microphone to give voice command</div>
            </div>

            <div class="presets">
                <span class="preset-chip" onclick="setAndExecute('Check system health and status')">🎙 Check system status</span>
                <span class="preset-chip" onclick="setAndExecute('Summarize active workspace files')">🎙 Summarize active workspace</span>
                <span class="preset-chip" onclick="setAndExecute('Open browser and search Python 3.10 release notes')">🎙 Open browser & search</span>
                <span class="preset-chip" onclick="setAndExecute('Run system performance report')">🎙 Run performance diagnostics</span>
            </div>

            <form class="prompt-form" onsubmit="handleFormSubmit(event)">
                <input type="text" id="promptInput" class="prompt-input" placeholder="Type or speak your voice command here..." required />
                <button type="submit" id="execBtn" class="exec-btn">Execute</button>
            </form>

            <div id="responseBox" class="response-box">
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155; padding-bottom:10px; margin-bottom:12px;">
                    <span style="font-weight:700; color:#38bdf8;">Astra Agent Workflow Result</span>
                    <span id="execDuration" style="font-size:0.85rem; color:#94a3b8;">Duration: -- ms</span>
                </div>
                <div style="margin-bottom:10px;">
                    <span style="font-size:0.85rem; color:#94a3b8;">Active Agents Triggered:</span>
                    <span id="agentsList" style="font-size:0.85rem; color:#a7f3d0; font-weight:600; margin-left:8px;">Planner Agent, Executor Agent</span>
                </div>
                <div id="responseText" style="line-height:1.6; color:#f8fafc; font-size:1.05rem;">
                </div>
            </div>
        </div>
    </div>

    <!-- Summary Metrics -->
    <div class="grid" id="summary-cards">
        <div class="card"><h3>System Health</h3><div class="value status-healthy" id="sys-status">LOADING...</div></div>
        <div class="card"><h3>Running Workflows</h3><div class="value" id="running-workflows">0</div></div>
        <div class="card"><h3>Total Traces</h3><div class="value" id="total-traces">0</div></div>
        <div class="card"><h3>Error Count</h3><div class="value status-unhealthy" id="error-count">0</div></div>
    </div>

    <h2 style="color:#38bdf8; font-size:1.3rem;">Subsystem Health Monitor</h2>
    <table id="health-table">
        <thead><tr><th>Subsystem</th><th>Status</th><th>Latency (ms)</th><th>Details</th></tr></thead>
        <tbody></tbody>
    </table>

    <h2 style="color:#38bdf8; font-size:1.3rem; margin-top:25px;">Recent Execution Logs</h2>
    <pre id="logs-view">Loading log records...</pre>

    <script>
        let recognition = null;
        let isListening = false;

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = 'en-US';

            recognition.onstart = function() {
                isListening = true;
                const btn = document.getElementById('micBtn');
                btn.classList.add('listening');
                document.getElementById('micStatus').innerText = '🎙 Listening to your voice... Speak now!';
                document.getElementById('micStatus').style.color = '#ef4444';
            };

            recognition.onresult = function(event) {
                let transcript = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    transcript += event.results[i][0].transcript;
                }
                document.getElementById('promptInput').value = transcript;
                if (event.results[0].isFinal) {
                    stopVoiceInput();
                    executeCommand(transcript);
                }
            };

            recognition.onerror = function(event) {
                stopVoiceInput();
                document.getElementById('micStatus').innerText = 'Voice input error: ' + event.error;
                document.getElementById('micStatus').style.color = '#f87171';
            };

            recognition.onend = function() { stopVoiceInput(); };
        }

        function toggleVoiceInput() {
            if (!recognition) {
                alert('Web Speech API is not supported in this browser. Please use Google Chrome, Microsoft Edge, or type your input.');
                return;
            }
            if (isListening) {
                recognition.stop();
            } else {
                try { recognition.start(); } catch (e) { recognition.stop(); }
            }
        }

        function stopVoiceInput() {
            isListening = false;
            const btn = document.getElementById('micBtn');
            if (btn) btn.classList.remove('listening');
            const status = document.getElementById('micStatus');
            if (status) {
                status.innerText = 'Click microphone to give voice command';
                status.style.color = '#94a3b8';
            }
        }

        function setAndExecute(text) {
            document.getElementById('promptInput').value = text;
            executeCommand(text);
        }

        function handleFormSubmit(e) {
            e.preventDefault();
            const prompt = document.getElementById('promptInput').value.trim();
            if (prompt) { executeCommand(prompt); }
        }

        async function executeCommand(promptText) {
            const execBtn = document.getElementById('execBtn');
            const responseBox = document.getElementById('responseBox');
            const responseText = document.getElementById('responseText');
            const execDuration = document.getElementById('execDuration');
            const agentsList = document.getElementById('agentsList');

            execBtn.innerText = 'Running...';
            execBtn.disabled = true;
            responseBox.style.display = 'block';
            responseText.innerText = 'Executing Astra Agent Workflow...';

            const startTime = performance.now();

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: promptText })
                });
                const data = await res.json();
                const duration = (performance.now() - startTime).toFixed(1);

                execDuration.innerText = 'Duration: ' + (data.duration_ms || duration) + ' ms';
                if (data.agents_used) {
                    agentsList.innerText = data.agents_used.join(', ');
                }

                const responseMsg = data.response || 'Workflow executed successfully.';
                responseText.innerText = responseMsg;

                if (document.getElementById('ttsToggle').checked && 'speechSynthesis' in window) {
                    window.speechSynthesis.cancel();
                    let speakText = responseMsg.split("Executed workflow for:")[0].trim();
                    speakText = speakText.replace(/\[API Error\]:[^.]*/g, "").trim();
                    if (!speakText) {
                        speakText = "Haan ji, bilkul! Main aapke saath Hinglish me natural female voice me baat kar sakti hu.";
                    }

                    const utterance = new SpeechSynthesisUtterance(speakText);
                    const femaleVoice = getFemaleVoice();
                    if (femaleVoice) {
                        utterance.voice = femaleVoice;
                    }
                    utterance.pitch = 1.2;
                    utterance.rate = 0.95;
                    window.speechSynthesis.speak(utterance);
                }
            } catch (err) {
                responseText.innerText = 'Error executing command: ' + err.message;
            } finally {
                execBtn.innerText = 'Execute';
                execBtn.disabled = false;
            }
        }

        let cachedFemaleVoice = null;
        function getFemaleVoice() {
            if (cachedFemaleVoice) return cachedFemaleVoice;
            if (!('speechSynthesis' in window)) return null;
            const voices = window.speechSynthesis.getVoices();
            if (!voices || voices.length === 0) return null;

            const female = voices.find(v => 
                (v.name.includes('Zira') || v.name.includes('Jenny') || v.name.includes('Aria') || 
                 v.name.includes('Sonia') || v.name.includes('Samantha') || v.name.includes('Victoria') || 
                 v.name.includes('Female') || v.name.includes('Google UK English Female') || 
                 v.name.includes('Google US English Female') || v.name.includes('Hindi') || v.name.includes('Natural'))
            ) || voices.find(v => v.lang.startsWith('en') || v.lang.startsWith('hi')) || voices[0];

            cachedFemaleVoice = female;
            return female;
        }

        if ('speechSynthesis' in window) {
            window.speechSynthesis.onvoiceschanged = function() {
                cachedFemaleVoice = null;
                getFemaleVoice();
            };
            getFemaleVoice();
        }

        async function fetchDashboard() {
            try {
                const res = await fetch('/dashboard/summary');
                const data = await res.json();
                document.getElementById('sys-status').innerText = (data.system.status || 'UNKNOWN').toUpperCase();
                document.getElementById('sys-status').className = 'value status-' + (data.system.status || 'healthy');
                document.getElementById('running-workflows').innerText = data.summary_cards.running_workflows;
                document.getElementById('total-traces').innerText = data.summary_cards.total_traces;
                document.getElementById('error-count').innerText = data.summary_cards.error_count;

                const tbody = document.querySelector('#health-table tbody');
                tbody.innerHTML = '';
                for (const [name, info] of Object.entries(data.system.subsystems || {})) {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `<td><b>${name}</b></td><td class="status-${info.state}">${info.state.toUpperCase()}</td><td>${info.latency_ms} ms</td><td>${info.details}</td>`;
                    tbody.appendChild(tr);
                }

                document.getElementById('logs-view').innerText = JSON.stringify(data.logs, null, 2);
            } catch (err) {
                console.error("Dashboard fetch error:", err);
            }
        }
        fetchDashboard();
        setInterval(fetchDashboard, 3000);
    </script>
    <script src="/avatar/static/animation_engine.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            if (window.initAstraAvatar) {
                window.initAstraAvatar('dash-avatar-container', {
                    manifestUrl: '/avatar/static/assets/sprite_manifest.json',
                    assetsDir: '/avatar/static/assets/'
                });
            }
        });
    </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)



@router.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """
    WebSocket endpoint streaming live dashboard updates to subscribers in real-time.
    """
    await websocket.accept()
    service = get_dashboard_service()
    try:
        while True:
            summary = service.get_dashboard_summary()
            await websocket.send_text(json.dumps(summary))
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        pass
    except Exception:
        await websocket.close()

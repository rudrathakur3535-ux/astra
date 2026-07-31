# Project Astra 🚀
> **Personal Desktop AI Operating System & Intelligent Virtual Assistant**

Project Astra is an advanced personal AI OS designed to provide natural voice interaction, persistent multi-session memory, direct PC/desktop control, browser tab automation, WhatsApp & email communications, computer vision screen understanding, intelligent code generation, and task execution.

---

## 🎯 Final 30-Day Vision

By Day 30, Project Astra will feature:
* 🎙 **Natural Voice Interaction**: Expressive, natural female voice outputs and real-time voice input listening.
* 🧠 **Long-Term Memory**: Session history, project tracking, and semantic search (SQLite + ChromaDB).
* 💻 **Desktop & PC Control**: Operating system task execution, window management, and application orchestration.
* 🌐 **Browser Automation**: Multi-tab control, web interactions, and page scraping using Playwright.
* 📂 **Workspace & Project Management**: Opening, editing, and managing local coding projects.
* 💬 **Messaging Integrations**: Automated WhatsApp messages & email dispatches.
* 👀 **Visual Perception**: Real-time screen capture, OCR, and vision analysis using OpenCV.
* 🧑‍💻 **Coding Assistant**: Intelligent code synthesis and agentic debugging.
* 🛡 **Safety & Guardrails**: Granular user confirmation and permissions before executing destructive or critical commands.

---

## 🛠 Tech Stack

| Component | Technology |
|---|---|
| **Language** | Python 3.10+ |
| **Brain / LLM Engine** | OpenAI GPT / Gemini / Claude |
| **Voice Input (STT)** | Whisper |
| **Voice Output (TTS)** | ElevenLabs |
| **Memory** | SQLite + ChromaDB |
| **GUI** | CustomTkinter |
| **PC Control** | PyAutoGUI |
| **Browser Control** | Playwright |
| **Vision & Screen** | OpenCV / PIL |
| **LLM Framework** | LangGraph / LangChain |
| **Local APIs** | FastAPI |

---

## 📂 Folder Architecture

```text
astra/
├── app/
│   ├── brain/          # LLM integrations, prompt engineering, agent orchestration (LangGraph)
│   ├── memory/         # Context management, SQLite history, ChromaDB vector storage
│   ├── voice/          # Whisper Speech-to-Text & ElevenLabs Text-to-Speech engines
│   ├── automation/     # Desktop control, PyAutoGUI, OS command executions
│   ├── vision/         # Screen capture, OpenCV image processing, multimodal vision
│   ├── browser/        # Playwright web automation, tab management, DOM interaction
│   ├── config/         # App settings, environment variable management (.env)
│   ├── database/       # DB models, connection initializers, migrations
│   └── logs/           # Application execution logs & audit trails
├── main.py             # Main entrypoint
├── requirements.txt    # Python dependencies
├── .env.example        # Environment configuration template
├── .gitignore          # Git exclusion rules
└── README.md           # Project documentation
```

### Folder Explanations in Detail

1. **`app/brain/`**: Contains the reasoning core of the AI. Manages API connections to LLMs (OpenAI GPT, Gemini, Claude), system prompts, decision routing, and LangGraph workflow nodes.
2. **`app/memory/`**: Manages short-term conversation context and long-term vector/relational persistence. Uses SQLite for structured chat logs and ChromaDB for semantic search across past conversations and project files.
3. **`app/voice/`**: Controls input audio capture and processing via Whisper, and natural speech synthesis via ElevenLabs.
4. **`app/automation/`**: Controls keyboard/mouse automation, application launching, filesystem operations, OS notifications, WhatsApp, and email actions.
5. **`app/vision/`**: Captures screen frames, processes images via OpenCV, and passes visual data to vision-enabled LLMs for real-time UI/screen understanding.
6. **`app/browser/`**: Runs headless or headed Playwright browser instances for searching, tab manipulation, and web task execution.
7. **`app/config/`**: Holds configuration models (e.g., `settings.py`), environment variable loaders (`python-dotenv`), and runtime settings.
8. **`app/database/`**: Defines SQLite database tables, connection helpers, and data access layers.
9. **`app/logs/`**: Stores structured runtime logs for debugging and auditing AI OS actions.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10 or higher
- Git

### 2. Environment Setup
Create and activate Python virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (Windows CMD)
venv\Scripts\activate.bat

# Activate (Linux/macOS)
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuration
Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```

### 5. Run Day 1 Verification
```bash
python main.py
```
Output:
```
[Project Astra] Initializing...
Hello AI
```

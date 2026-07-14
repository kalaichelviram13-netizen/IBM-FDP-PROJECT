# AI Legal Aid Multi-Agent System

> An intelligent, multi-agent platform that makes legal assistance accessible, affordable, and understandable for individuals and small businesses.

---

## 🌟 The Challenge

Access to legal advice is often **expensive, time-consuming, and complex**. Individuals and small businesses struggle to understand contracts, rights, and compliance due to scattered resources and legal jargon. Traditional legal aid systems are limited by the availability of experts and lack real-time support.

**This system addresses that gap** by deploying a coordinated team of specialised AI agents — powered by IBM watsonx.ai — that collaboratively analyse, research, simplify, and advise on legal matters in real time.

---

## 🏗️ System Architecture

```
                        ┌─────────────────────────────┐
     User Query  ──────▶│   Legal Aid Orchestrator     │
     + Document         │  (Intent Classifier + Router)│
                        └──────────────┬──────────────┘
                                       │ routes to
               ┌───────────┬───────────┼───────────┬───────────┐
               ▼           ▼           ▼           ▼           
        ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   
        │ Contract │ │  Rights  │ │Document  │ │  Case    │   
        │ Analysis │ │Compliance│ │Simplifier│ │Researcher│   
        └──────────┘ └──────────┘ └──────────┘ └──────────┘   
               │           │           │           │           
               └───────────┴───────────┴───────────┘           
                                   │ synthesises
                                   ▼
                            Final Response
```

### Agents

| Agent | Role | Key Capabilities |
|-------|------|-----------------|
| **⚖️ Orchestrator** | Coordinator | Intent classification, routing, response synthesis |
| **📄 Contract Analysis** | Specialist | Risk flags, obligations, missing clauses, risk scoring |
| **🏛️ Rights & Compliance** | Specialist | Consumer, employment, GDPR, business compliance |
| **📝 Document Simplifier** | Specialist | Plain-English translation, jargon glossary, complexity rating |
| **🔍 Case Researcher** | Specialist | Case law, statutory references, legal precedents |

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone <repo-url>
cd ai-legal-aid
pip install -r requirements.txt
```

### 2. Configure Credentials

```bash
cp .env.example .env
# Edit .env with your IBM watsonx.ai credentials
```

Required environment variables:
```
WATSONX_API_KEY=your_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

> **No API key?** The system runs in **Mock/Demo mode** automatically — great for testing!

### 3. Run

```bash
# Web UI (recommended)
streamlit run streamlit_app.py

# Or via app.py
python app.py           # launches Streamlit
python app.py --cli     # interactive terminal
python app.py --demo    # run demo queries
```

---

## 💻 Usage Examples

### Web Interface
1. Open `http://localhost:8501`
2. Type your legal question or upload a PDF/DOCX contract
3. Optionally set jurisdiction and user type in the sidebar
4. Receive structured analysis from the appropriate specialist agents

### CLI
```
You: What are my rights if my landlord won't fix the heating?

Agent(s): rights_compliance
─────────────────────────────────────────
**Applicable Rights / Obligations**
Under the Landlord and Tenant Act 1985, your landlord is legally
required to maintain the structure and exterior of the property...
```

### Python API
```python
from agents.orchestrator import LegalAidOrchestrator

orchestrator = LegalAidOrchestrator()

result = orchestrator.process(
    query="What risks should I look for in this freelance agreement?",
    document_text="...contract text...",
    context={"jurisdiction": "United Kingdom", "user_type": "freelancer"},
)

print(result.final_response)
print(f"Agents used: {result.intents_detected}")
print(f"Response time: {result.total_elapsed:.2f}s")
```

---

## 📂 Project Structure

```
├── agents/
│   ├── __init__.py
│   ├── base_agent.py           # Abstract base class (AgentInput, AgentOutput)
│   ├── orchestrator.py         # Intent classifier + multi-agent router
│   ├── contract_analyst.py     # Contract Analysis Agent
│   ├── rights_compliance.py    # Legal Rights & Compliance Agent
│   ├── document_simplifier.py  # Document Simplification Agent
│   └── case_researcher.py      # Case Research Agent
├── utils/
│   ├── __init__.py
│   ├── llm_client.py           # Unified LLM interface (watsonx / OpenAI / mock)
│   ├── document_parser.py      # PDF, DOCX, TXT parser
│   └── logger.py               # Structured logging
├── prompts/
│   └── system_prompts.py       # System prompt reference library
├── tests/
│   └── test_system.py          # Full test suite (mock mode, no API keys needed)
├── app.py                      # Main entry point (CLI / demo / web launcher)
├── streamlit_app.py            # Streamlit web UI
├── config.py                   # Centralised configuration
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔑 Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Multi-agent architecture** | Each specialist agent is independently optimised (temperature, prompt, parsing) for its domain |
| **Orchestrator pattern** | Single entry point keeps the API clean; clients never need to know which agent ran |
| **Graceful degradation to mock** | Works out-of-the-box without API keys for demos and testing |
| **Memory per agent** | Each agent retains recent conversation turns for contextual follow-ups |
| **Synthesis layer** | When two agents are invoked, their outputs are blended into one coherent response |

---

## 🧪 Running Tests

```bash
python -m pytest tests/test_system.py -v
# or
python tests/test_system.py
```

All tests run in **mock mode** — no API keys or internet connection required.

---

## ⚠️ Disclaimer

This system provides **legal information** only — not legal advice. Always consult a qualified solicitor or legal professional before making decisions on important legal matters.

---

## 🛠️ Built With

- [IBM watsonx.ai](https://www.ibm.com/watsonx) — Primary LLM provider (IBM Granite)
- [Streamlit](https://streamlit.io) — Web interface
- [pypdf](https://github.com/py-pdf/pypdf) — PDF parsing
- [python-docx](https://python-docx.readthedocs.io) — DOCX parsing

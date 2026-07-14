"""
AI Legal Aid Multi-Agent System — Streamlit Web UI
====================================================
Full-featured chat interface with document upload, agent routing,
and session history.
"""

from __future__ import annotations

import sys
import os
import uuid
from pathlib import Path

# --- Load credentials from .env / .env.example before any agent imports ---
def _load_env() -> None:
    root = Path(__file__).resolve().parent
    for candidate in (".env", ".env.example"):
        env_path = root / candidate
        if env_path.exists():
            with open(env_path, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, value = line.partition("=")
                    key, value = key.strip(), value.strip()
                    if key not in os.environ and "your_" not in value.lower():
                        os.environ[key] = value
            break

_load_env()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from agents.orchestrator import LegalAidOrchestrator
from utils.document_parser import parse_document, truncate_text
from config import APP_CONFIG, AGENT_ROLES

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="AI Legal Aid Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    /* Main layout */
    .main .block-container { padding-top: 1.5rem; max-width: 1100px; }

    /* Chat message bubbles */
    .user-bubble {
        background: #e8f0fe;
        border-radius: 16px 16px 4px 16px;
        padding: 0.75rem 1.1rem;
        margin: 0.4rem 0;
        max-width: 85%;
        margin-left: auto;
        color: #1a1a2e;
        font-size: 0.95rem;
    }
    .assistant-bubble {
        background: #f7f8fa;
        border: 1px solid #e5e7eb;
        border-radius: 16px 16px 16px 4px;
        padding: 0.85rem 1.1rem;
        margin: 0.4rem 0;
        max-width: 95%;
        color: #1f2328;
        font-size: 0.95rem;
    }

    /* Agent badge */
    .agent-badge {
        display: inline-block;
        background: #3b82d4;
        color: white;
        border-radius: 12px;
        padding: 2px 10px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    /* Sidebar agent cards */
    .agent-card {
        background: #f7f8fa;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 0.65rem 0.85rem;
        margin-bottom: 0.5rem;
    }
    .agent-card h4 { margin: 0 0 2px 0; font-size: 0.9rem; color: #1f2328; }
    .agent-card p  { margin: 0; font-size: 0.78rem; color: #57606a; }

    /* Status indicator */
    .status-ok  { color: #22863a; font-weight: 600; }
    .status-err { color: #cb2431; font-weight: 600; }

    /* Divider */
    hr.section { border: none; border-top: 1px solid #e5e7eb; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

def _init_session() -> None:
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = LegalAidOrchestrator()
    if "messages" not in st.session_state:
        st.session_state.messages = []  # list of {"role": "user"|"assistant", "content": str, "meta": dict}
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())[:8]
    if "uploaded_doc_text" not in st.session_state:
        st.session_state.uploaded_doc_text = None
    if "uploaded_filename" not in st.session_state:
        st.session_state.uploaded_filename = None


_init_session()


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## ⚖️ AI Legal Aid")
    st.caption(f"v{APP_CONFIG.version} · Session `{st.session_state.session_id}`")
    st.markdown('<hr class="section">', unsafe_allow_html=True)

    # --- Document Upload ---
    st.markdown("### 📎 Upload Document")
    uploaded_file = st.file_uploader(
        "Upload a contract or legal document",
        type=["pdf", "txt", "docx"],
        help="Max 10 MB. Supported: PDF, TXT, DOCX",
    )
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        doc_text = parse_document(file_bytes, filename=uploaded_file.name)
        st.session_state.uploaded_doc_text = truncate_text(doc_text, 8000)
        st.session_state.uploaded_filename = uploaded_file.name
        st.success(f"✅ Loaded: **{uploaded_file.name}** ({len(doc_text):,} chars)")

    if st.session_state.uploaded_doc_text:
        if st.button("🗑️ Remove Document", use_container_width=True):
            st.session_state.uploaded_doc_text = None
            st.session_state.uploaded_filename = None
            st.rerun()

    st.markdown('<hr class="section">', unsafe_allow_html=True)

    # --- Context Settings ---
    st.markdown("### ⚙️ Settings")
    jurisdiction = st.selectbox(
        "Jurisdiction",
        ["United Kingdom", "European Union", "United States", "India", "Australia", "Other"],
        index=0,
    )
    user_type = st.selectbox(
        "I am a ...",
        ["Individual / Consumer", "Small Business Owner", "Employee", "Landlord / Tenant",
         "Student / Researcher", "Legal Professional"],
        index=0,
    )

    st.markdown('<hr class="section">', unsafe_allow_html=True)

    # --- Specialist Agents ---
    st.markdown("### 🤖 Specialist Agents")
    for role_key, role_info in AGENT_ROLES.items():
        if role_key == "orchestrator":
            continue
        st.markdown(
            f'<div class="agent-card">'
            f'<h4>{role_info["emoji"]} {role_info["name"]}</h4>'
            f'<p>{role_info["description"]}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="section">', unsafe_allow_html=True)

    # --- Session Controls ---
    st.markdown("### 🔄 Session")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🆕 New", use_container_width=True):
            st.session_state.orchestrator.clear_session()
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())[:8]
            st.session_state.uploaded_doc_text = None
            st.session_state.uploaded_filename = None
            st.rerun()
    with col2:
        history = st.session_state.orchestrator.get_session_history()
        st.metric("Queries", len(history))

    st.markdown('<hr class="section">', unsafe_allow_html=True)
    st.caption("⚠️ *This tool provides legal information only — not legal advice. Always consult a qualified solicitor for important matters.*")


# ---------------------------------------------------------------------------
# Main panel — header
# ---------------------------------------------------------------------------

st.markdown("## ⚖️ AI Legal Aid Multi-Agent System")
st.markdown(
    "Ask any legal question, upload a document, or request plain-English explanations. "
    "Specialist AI agents will collaborate to provide a comprehensive response."
)

if st.session_state.uploaded_filename:
    st.info(f"📄 Active document: **{st.session_state.uploaded_filename}** "
            f"({len(st.session_state.uploaded_doc_text or ''):,} chars loaded)")

st.markdown('<hr class="section">', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Chat history display
# ---------------------------------------------------------------------------

chat_container = st.container()

with chat_container:
    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align:center; padding:2rem 0; color:#57606a;">
            <p style="font-size:2rem">⚖️</p>
            <p style="font-size:1.05rem; font-weight:600;">Welcome to AI Legal Aid</p>
            <p>Start by asking a legal question below, or upload a document on the left.</p>
            <br>
            <b>Try asking:</b><br>
            "What should I look for in a freelance contract?"<br>
            "What are my rights if I've been unfairly dismissed?"<br>
            "Explain this GDPR clause in plain English"<br>
            "What are the key cases on negligence?"
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="user-bubble">🧑 {msg["content"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                meta = msg.get("meta", {})
                agents_used = ", ".join(meta.get("agents", ["Legal Aid"]))
                elapsed = meta.get("elapsed", 0)
                badge = f'<span class="agent-badge">🤖 {agents_used} · {elapsed:.1f}s</span>'
                st.markdown(
                    f'<div class="assistant-bubble">{badge}<br>{msg["content"]}</div>',
                    unsafe_allow_html=True,
                )


# ---------------------------------------------------------------------------
# Quick-start example queries
# ---------------------------------------------------------------------------

if not st.session_state.messages:
    st.markdown("#### 💡 Quick Examples")
    ex_cols = st.columns(2)
    examples = [
        ("📄 Contract Review",      "Review my employment contract and identify any unfair clauses or risks I should be aware of."),
        ("🏛️ Know Your Rights",    "What are my rights as a tenant if my landlord refuses to carry out essential repairs?"),
        ("📝 Plain English",        "Simplify this legal jargon: 'Force majeure events shall absolve the obligor of liability for non-performance.'"),
        ("🔍 Case Research",        "What are the landmark UK cases on data protection and individual privacy rights?"),
    ]
    for i, (label, query_text) in enumerate(examples):
        col = ex_cols[i % 2]
        with col:
            if st.button(label, use_container_width=True, key=f"ex_{i}"):
                st.session_state["prefill_query"] = query_text
                st.rerun()


# ---------------------------------------------------------------------------
# Input area
# ---------------------------------------------------------------------------

prefill = st.session_state.pop("prefill_query", "")

with st.form("chat_form", clear_on_submit=True):
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        user_input = st.text_area(
            "Your legal question",
            value=prefill,
            placeholder="Describe your legal situation or ask a question…",
            height=90,
            label_visibility="collapsed",
        )
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Send ➤", use_container_width=True, type="primary")


# ---------------------------------------------------------------------------
# Process submission
# ---------------------------------------------------------------------------

if submitted and user_input.strip():
    query = user_input.strip()

    # Append user message to history
    st.session_state.messages.append({"role": "user", "content": query})

    # Build context dict
    context = {
        "jurisdiction": jurisdiction,
        "user_type": user_type,
    }

    # Show spinner while processing
    with st.spinner("⚖️ Legal agents are analysing your query…"):
        result = st.session_state.orchestrator.process(
            query=query,
            document_text=st.session_state.uploaded_doc_text,
            context=context,
            session_id=st.session_state.session_id,
            synthesise=True,
        )

    # Format agent names for display
    agent_display_names = []
    for intent in result.intents_detected:
        role_key_map = {
            "contract_analysis":      "contract_analyst",
            "rights_compliance":      "rights_compliance",
            "document_simplification": "document_simplifier",
            "case_research":          "case_researcher",
        }
        rk = role_key_map.get(intent, intent)
        info = AGENT_ROLES.get(rk, {})
        agent_display_names.append(
            f"{info.get('emoji', '🤖')} {info.get('name', intent)}"
        )

    # Convert markdown to HTML-safe format for the bubble (Streamlit markdown inside HTML)
    response_text = result.final_response

    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text,
        "meta": {
            "agents": agent_display_names,
            "elapsed": result.total_elapsed,
            "intents": result.intents_detected,
        },
    })

    st.rerun()


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.markdown('<hr class="section">', unsafe_allow_html=True)
st.markdown(
    "<div style='text-align:center; color:#57606a; font-size:0.78rem;'>"
    "AI Legal Aid Multi-Agent System · Built with IBM watsonx.ai · "
    "For informational purposes only — not a substitute for professional legal advice."
    "</div>",
    unsafe_allow_html=True,
)

"""
AI Legal Aid Multi-Agent System
================================
Main application entry point.
Supports three run modes:
  1. CLI  — py app.py --cli
  2. Demo — py app.py --demo
  3. Web  — py app.py  (default, launches Streamlit)
"""

from __future__ import annotations

import argparse
import sys
import os
from pathlib import Path

# ── 1. Project root on path ──────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# ── 2. Load credentials from .env.example (no .env needed) ──────────────────
def _load_env() -> None:
    for candidate in (".env", ".env.example"):
        env_path = ROOT / candidate
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

from agents.orchestrator import LegalAidOrchestrator
from utils.logger import setup_logging

logger = setup_logging()


# ---------------------------------------------------------------------------
# CLI Mode
# ---------------------------------------------------------------------------

def run_cli() -> None:
    """Interactive command-line interface."""
    orchestrator = LegalAidOrchestrator()
    print("\n" + "=" * 60)
    print("  [Legal Aid] AI Legal Aid Multi-Agent System")
    print("=" * 60)
    print("Type your legal question and press Enter.")
    print("Commands: 'clear' = new session | 'history' = view history | 'quit' = exit\n")

    while True:
        try:
            query = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not query:
            continue
        if query.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        if query.lower() == "clear":
            orchestrator.clear_session()
            print("[Session cleared]\n")
            continue
        if query.lower() == "history":
            history = orchestrator.get_session_history()
            if not history:
                print("[No history yet]\n")
            else:
                for i, h in enumerate(history, 1):
                    print(f"  [{i}] Agents: {h['intents']} | Q: {h['query'][:80]}")
                print()
            continue

        result = orchestrator.process(query=query)
        print(f"\n{'─' * 60}")
        print(f"Agent(s): {', '.join(result.intents_detected)}")
        print(f"{'─' * 60}")
        print(result.final_response)
        print(f"{'─' * 60}\n")


# ---------------------------------------------------------------------------
# Demo Mode — runs a set of pre-defined queries
# ---------------------------------------------------------------------------

DEMO_QUERIES = [
    {
        "title": "Contract Risk Assessment",
        "query": "I have a freelance contract with an extremely broad indemnification clause. What should I look out for?",
    },
    {
        "title": "Employee Rights",
        "query": "My employer has just told me I'm being made redundant. What are my legal rights?",
    },
    {
        "title": "GDPR Compliance",
        "query": "We run a small e-commerce site. What GDPR obligations do we have and what are the risks of non-compliance?",
    },
    {
        "title": "Case Research — Negligence",
        "query": "What are the key legal precedents for negligence and duty of care in English law?",
    },
    {
        "title": "Document Simplification",
        "query": "Explain this clause in plain English: 'The licensor hereby grants the licensee a non-exclusive, non-transferable, revocable licence to use the software solely for the licensee's internal business purposes.'",
    },
]


def run_demo() -> None:
    """Run pre-defined demo queries and print results."""
    orchestrator = LegalAidOrchestrator()
    print("\n" + "=" * 60)
    print("  [Legal Aid] AI Legal Aid Multi-Agent System - DEMO MODE")
    print("=" * 60 + "\n")

    for i, demo in enumerate(DEMO_QUERIES, 1):
        print(f"[{i}/{len(DEMO_QUERIES)}] {demo['title']}")
        print(f"Q: {demo['query']}\n")
        result = orchestrator.process(query=demo["query"])
        print(f"Agents: {', '.join(result.intents_detected)}")
        print(f"Time:   {result.total_elapsed:.2f}s")
        print(f"─" * 60)
        print(result.final_response)
        print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# Streamlit Web Mode
# ---------------------------------------------------------------------------

def run_streamlit() -> None:
    """Launch the Streamlit web interface."""
    import subprocess
    streamlit_app = str(ROOT / "streamlit_app.py")
    print("\n[Legal Aid] Starting AI Legal Aid Web UI...")
    print("   Open your browser at: http://localhost:8501\n")
    subprocess.run(
        [
            sys.executable, "-m", "streamlit", "run", streamlit_app,
            "--browser.gatherUsageStats", "false",
            "--server.headless", "false",
        ],
        check=False,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Legal Aid Multi-Agent System")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--cli",  action="store_true", help="Run interactive CLI mode")
    group.add_argument("--demo", action="store_true", help="Run demo queries and exit")
    group.add_argument("--web",  action="store_true", help="Launch Streamlit web UI (default)")
    args = parser.parse_args()

    if args.cli:
        run_cli()
    elif args.demo:
        run_demo()
    else:
        # Default: Streamlit web
        run_streamlit()

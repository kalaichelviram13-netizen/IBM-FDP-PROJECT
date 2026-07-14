"""
AI Legal Aid Multi-Agent System — Configuration
================================================
Central configuration for all agents, models, and system settings.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# IBM watsonx / OpenAI model settings
# ---------------------------------------------------------------------------

@dataclass
class ModelConfig:
    """LLM provider and model identifiers."""
    provider: str = "ibm_watsonx"           # "ibm_watsonx" | "openai" | "mock"
    model_id: str = "ibama/granite-13b-chat-v2"
    temperature: float = 0.2
    max_tokens: int = 2048
    top_p: float = 0.9


@dataclass
class WatsonxConfig:
    """IBM watsonx.ai credentials (read from environment)."""
    api_key: str = field(default_factory=lambda: os.getenv("WATSONX_API_KEY", ""))
    project_id: str = field(default_factory=lambda: os.getenv("WATSONX_PROJECT_ID", ""))
    url: str = field(default_factory=lambda: os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com"))


@dataclass
class OpenAIConfig:
    """OpenAI credentials (fallback provider)."""
    api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    model: str = "gpt-4o-mini"


# ---------------------------------------------------------------------------
# Agent settings
# ---------------------------------------------------------------------------

@dataclass
class AgentConfig:
    """Per-agent runtime parameters."""
    max_iterations: int = 5
    timeout_seconds: int = 60
    verbose: bool = True
    memory_enabled: bool = True


# ---------------------------------------------------------------------------
# Application settings
# ---------------------------------------------------------------------------

@dataclass
class AppConfig:
    """Streamlit / app-level settings."""
    title: str = "AI Legal Aid Multi-Agent System"
    version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    max_file_size_mb: int = 10
    supported_doc_types: tuple = ("pdf", "txt", "docx")


# ---------------------------------------------------------------------------
# Singleton accessors
# ---------------------------------------------------------------------------

MODEL_CONFIG = ModelConfig()
WATSONX_CONFIG = WatsonxConfig()
OPENAI_CONFIG = OpenAIConfig()
AGENT_CONFIG = AgentConfig()
APP_CONFIG = AppConfig()


# ---------------------------------------------------------------------------
# Agent role registry
# ---------------------------------------------------------------------------

AGENT_ROLES = {
    "orchestrator": {
        "name": "Legal Aid Orchestrator",
        "description": "Routes user queries to the most appropriate specialist agents and synthesises final responses.",
        "emoji": "⚖️",
    },
    "contract_analyst": {
        "name": "Contract Analysis Agent",
        "description": "Reviews contract clauses, identifies risks, obligations, and unfair terms.",
        "emoji": "📄",
    },
    "rights_compliance": {
        "name": "Legal Rights & Compliance Agent",
        "description": "Advises on legal rights, regulatory obligations, and compliance requirements.",
        "emoji": "🏛️",
    },
    "document_simplifier": {
        "name": "Document Simplification Agent",
        "description": "Translates complex legal text into plain, accessible language.",
        "emoji": "📝",
    },
    "case_researcher": {
        "name": "Case Research Agent",
        "description": "Retrieves relevant case law, precedents, and statutory references.",
        "emoji": "🔍",
    },
}

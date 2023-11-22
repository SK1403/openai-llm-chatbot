#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
##
# Description:-
#
#       Configuration management module for Azure OpenAI and OpenAI LLM
#       conversational chatbot, including model parameters, Azure Entra ID
#       settings, deployment endpoints, and system persona configurations.
#
##
# Development date    Developed by       Comments
# ----------------    ------------       ---------
# 04/11/2023          Saddam Khan        Initial implementation
# 22/11/2023          Saddam Khan        Added Azure OpenAI API version and persona presets
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os
from dataclasses import dataclass, field
from typing import Dict
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


PERSONA_PRESETS: Dict[str, str] = {
    "Cloud Solutions Architect": (
        "You are an expert Principal Cloud Solutions Architect specializing in Azure, "
        "OpenAI, LangChain, and enterprise distributed systems. Provide clear, actionable, "
        "and architecturally sound answers with production-ready code examples."
    ),
    "Python AI Engineer": (
        "You are a Senior Python AI Engineer skilled in LangChain, OpenAI SDK, async "
        "pipelines, vector databases, and software engineering best practices. Write clean, "
        "well-structured Python code with concise explanations."
    ),
    "DevOps & SRE Specialist": (
        "You are a Principal DevOps and Site Reliability Engineer focusing on Kubernetes, "
        "Terraform, Azure Monitor, CI/CD automation, and cloud infrastructure resilience."
    ),
    "General Enterprise Assistant": (
        "You are a helpful, accurate, and concise enterprise AI assistant powered by Azure OpenAI "
        "and LangChain. Provide structured, reliable answers to technical and business questions."
    ),
}


@dataclass
class ChatbotConfig:
    """Centralized configuration for Azure OpenAI and OpenAI LLM Chatbot."""

    provider: str = field(
        default_factory=lambda: os.getenv("LLM_PROVIDER", "azure_openai")
    )
    azure_openai_api_key: str = field(
        default_factory=lambda: os.getenv("AZURE_OPENAI_API_KEY", "")
    )
    azure_openai_endpoint: str = field(
        default_factory=lambda: os.getenv(
            "AZURE_OPENAI_ENDPOINT", "https://enterprise-openai-prod.openai.azure.com/"
        )
    )
    azure_openai_deployment: str = field(
        default_factory=lambda: os.getenv(
            "AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4-1106-preview"
        )
    )
    azure_openai_api_version: str = field(
        default_factory=lambda: os.getenv(
            "AZURE_OPENAI_API_VERSION", "2023-12-01-preview"
        )
    )
    use_azure_ad: bool = field(
        default_factory=lambda: os.getenv("USE_AZURE_AD_AUTH", "false").lower()
        == "true"
    )
    openai_api_key: str = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", "")
    )
    openai_model_name: str = field(
        default_factory=lambda: os.getenv("OPENAI_MODEL_NAME", "gpt-4-1106-preview")
    )
    temperature: float = field(
        default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.3"))
    )
    max_tokens: int = field(
        default_factory=lambda: int(os.getenv("LLM_MAX_TOKENS", "2048"))
    )
    streaming: bool = field(
        default_factory=lambda: os.getenv("LLM_STREAMING", "true").lower() == "true"
    )
    default_persona: str = field(
        default_factory=lambda: os.getenv(
            "DEFAULT_PERSONA", "Cloud Solutions Architect"
        )
    )

    def get_system_prompt(self, persona_name: str = "") -> str:
        """Resolve system prompt instruction for the selected persona."""
        selected = persona_name or self.default_persona
        return PERSONA_PRESETS.get(
            selected, PERSONA_PRESETS["Cloud Solutions Architect"]
        )

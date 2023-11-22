#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
##
# Description:-
#
#       Azure Entra ID (Azure AD) token provider and credential validation
#       module for enterprise Azure OpenAI and OpenAI API deployments.
#
##
# Development date    Developed by       Comments
# ----------------    ------------       ---------
# 04/11/2023          Saddam Khan        Initial implementation
# 22/11/2023          Saddam Khan        Added Azure DefaultAzureCredential bearer token provider
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from typing import Callable, Optional, Tuple
from config import ChatbotConfig


def get_azure_ad_token_provider() -> Optional[Callable[[], str]]:
    """Return an Azure AD bearer token callable using DefaultAzureCredential."""
    try:
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider

        credential = DefaultAzureCredential()
        return get_bearer_token_provider(
            credential, "https://cognitiveservices.azure.com/.default"
        )
    except Exception:
        return None


def validate_provider_credentials(config: ChatbotConfig) -> Tuple[bool, str]:
    """Validate whether Azure OpenAI or OpenAI credentials are configured."""
    if config.provider == "azure_openai":
        if config.use_azure_ad:
            token_provider = get_azure_ad_token_provider()
            if token_provider is not None:
                return True, "Azure Entra ID (DefaultAzureCredential) Active"
            return False, "Azure Entra ID token provider unavailable"
        if config.azure_openai_api_key and config.azure_openai_endpoint:
            return True, "Azure OpenAI API Key Configured"
        return (
            False,
            "Missing AZURE_OPENAI_API_KEY or AZURE_OPENAI_ENDPOINT (Simulation Mode)",
        )
    else:
        if config.openai_api_key:
            return True, "OpenAI API Key Configured"
        return False, "Missing OPENAI_API_KEY (Simulation Mode)"

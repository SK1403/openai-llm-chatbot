#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
##
# Description:-
#
#       Package initializer for Azure OpenAI and OpenAI authentication
#       and telemetry utility functions.
#
##
# Development date    Developed by       Comments
# ----------------    ------------       ---------
# 04/11/2023          Saddam Khan        Initial implementation
# 22/11/2023          Saddam Khan        Exported Azure credential helper functions
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from utils.auth import get_azure_ad_token_provider, validate_provider_credentials

__all__ = ["get_azure_ad_token_provider", "validate_provider_credentials"]

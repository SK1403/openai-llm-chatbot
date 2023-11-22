#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
##
# Description:-
#
#       Core LangChain conversational engine integrating AzureChatOpenAI
#       and ChatOpenAI with multi-turn session memory and token streaming.
#
##
# Development date    Developed by       Comments
# ----------------    ------------       ---------
# 04/11/2023          Saddam Khan        Initial implementation
# 22/11/2023          Saddam Khan        Integrated RunnableWithMessageHistory and streaming generator
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import time
from typing import Dict, Generator, List, Optional
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import AzureChatOpenAI, ChatOpenAI

from config import ChatbotConfig
from utils.auth import get_azure_ad_token_provider, validate_provider_credentials


class OpenAILLMChatbot:
    """Enterprise conversational chatbot powered by Azure OpenAI and LangChain."""

    def __init__(self, config: Optional[ChatbotConfig] = None) -> None:
        self.config = config or ChatbotConfig()
        self.sessions: Dict[str, InMemoryChatMessageHistory] = {}
        self.is_live_mode, self.status_message = validate_provider_credentials(
            self.config
        )

    def _get_session_history(self, session_id: str) -> InMemoryChatMessageHistory:
        """Retrieve or initialize an in-memory conversation history for a session."""
        if session_id not in self.sessions:
            self.sessions[session_id] = InMemoryChatMessageHistory()
        return self.sessions[session_id]

    def clear_session(self, session_id: str) -> None:
        """Clear conversation history for the given session ID."""
        if session_id in self.sessions:
            self.sessions[session_id].clear()

    def get_history_messages(self, session_id: str) -> List[BaseMessage]:
        """Return the list of messages stored in the session history."""
        return self._get_session_history(session_id).messages

    def _build_llm(self):
        """Instantiate AzureChatOpenAI or ChatOpenAI based on configuration."""
        if self.config.provider == "azure_openai":
            if self.config.use_azure_ad:
                token_provider = get_azure_ad_token_provider()
                return AzureChatOpenAI(
                    azure_endpoint=self.config.azure_openai_endpoint,
                    azure_deployment=self.config.azure_openai_deployment,
                    api_version=self.config.azure_openai_api_version,
                    azure_ad_token_provider=token_provider,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    streaming=self.config.streaming,
                )
            return AzureChatOpenAI(
                azure_endpoint=self.config.azure_openai_endpoint,
                azure_deployment=self.config.azure_openai_deployment,
                api_version=self.config.azure_openai_api_version,
                api_key=self.config.azure_openai_api_key,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                streaming=self.config.streaming,
            )
        return ChatOpenAI(
            model=self.config.openai_model_name,
            api_key=self.config.openai_api_key,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            streaming=self.config.streaming,
        )

    def _build_chain(self, persona_name: str):
        """Construct the LangChain RunnableWithMessageHistory pipeline."""
        system_prompt = self.config.get_system_prompt(persona_name)
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
            ]
        )
        llm = self._build_llm()
        runnable = prompt | llm
        return RunnableWithMessageHistory(
            runnable,
            self._get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        )

    def chat(
        self,
        user_input: str,
        session_id: str = "default-session",
        persona_name: Optional[str] = None,
    ) -> str:
        """Execute a synchronous chat turn and return the assistant response."""
        selected_persona = persona_name or self.config.default_persona
        if not self.is_live_mode:
            history = self._get_session_history(session_id)
            history.add_user_message(user_input)
            simulated_reply = self._generate_simulated_response(
                user_input, selected_persona
            )
            history.add_ai_message(simulated_reply)
            return simulated_reply

        chain = self._build_chain(selected_persona)
        response = chain.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": session_id}},
        )
        return response.content

    def stream_chat(
        self,
        user_input: str,
        session_id: str = "default-session",
        persona_name: Optional[str] = None,
    ) -> Generator[str, None, None]:
        """Stream response tokens for real-time interactive chat UI."""
        selected_persona = persona_name or self.config.default_persona
        if not self.is_live_mode:
            history = self._get_session_history(session_id)
            history.add_user_message(user_input)
            simulated_reply = self._generate_simulated_response(
                user_input, selected_persona
            )
            history.add_ai_message(simulated_reply)
            for token in simulated_reply.split(" "):
                yield token + " "
                time.sleep(0.02)
            return

        chain = self._build_chain(selected_persona)
        for chunk in chain.stream(
            {"input": user_input},
            config={"configurable": {"session_id": session_id}},
        ):
            if hasattr(chunk, "content") and chunk.content:
                yield chunk.content

    def _generate_simulated_response(
        self, user_input: str, persona_name: str
    ) -> str:
        """Generate a realistic architectural response when running in offline/demo mode."""
        return (
            f"**[{persona_name} | Azure OpenAI ({self.config.azure_openai_deployment})]**\n\n"
            f"Here is an enterprise solution addressing your query: *\"{user_input}\"*\n\n"
            "### Recommended Architecture & Implementation\n"
            "1. **Authentication Layer**: Use `DefaultAzureCredential` via `azure-identity` for zero-secret "
            "managed identity authentication to Azure OpenAI endpoints.\n"
            "2. **LangChain Orchestration**: Bind `AzureChatOpenAI` with `ChatPromptTemplate` and "
            "`RunnableWithMessageHistory` to maintain stateful multi-turn context.\n"
            "3. **Resilience & Observability**: Configure exponential backoff retries and token usage telemetry.\n\n"
            "```python\n"
            "from langchain_openai import AzureChatOpenAI\n"
            "from azure.identity import DefaultAzureCredential, get_bearer_token_provider\n\n"
            "token_provider = get_bearer_token_provider(\n"
            "    DefaultAzureCredential(), \"https://cognitiveservices.azure.com/.default\"\n"
            ")\n"
            "llm = AzureChatOpenAI(\n"
            "    azure_deployment=\"gpt-4-1106-preview\",\n"
            "    api_version=\"2023-12-01-preview\",\n"
            "    azure_ad_token_provider=token_provider,\n"
            "    streaming=True\n"
            ")\n"
            "```"
        )

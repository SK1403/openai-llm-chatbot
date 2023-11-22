#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
##
# Description:-
#
#       Streamlit web user interface for the Azure OpenAI & LangChain
#       conversational chatbot with real-time token streaming and session controls.
#
##
# Development date    Developed by       Comments
# ----------------    ------------       ---------
# 04/11/2023          Saddam Khan        Initial implementation
# 22/11/2023          Saddam Khan        Added provider switcher, persona selector, and streaming chat UI
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import uuid
import streamlit as st
from config import ChatbotConfig, PERSONA_PRESETS
from chatbot import OpenAILLMChatbot


def init_session_state() -> None:
    """Initialize Streamlit session state variables."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = f"azure-session-{str(uuid.uuid4())[:8]}"
    if "config" not in st.session_state:
        st.session_state.config = ChatbotConfig()
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = OpenAILLMChatbot(st.session_state.config)
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Welcome to the **Azure OpenAI & LangChain LLM Chatbot**! "
                    "Select your Azure deployment or OpenAI model in the sidebar and ask any question."
                ),
            }
        ]


def main() -> None:
    """Render the Streamlit conversational web interface."""
    st.set_page_config(
        page_title="OpenAI LLM Conversational Chatbot",
        page_icon="⚡",
        layout="wide",
    )
    init_session_state()

    with st.sidebar:
        st.title("OpenAI LLM Conversational Chatbot")
        st.caption("LangChain Conversational Engine")

        provider = st.selectbox(
            "LLM Provider",
            options=["azure_openai", "openai"],
            format_func=lambda x: "Azure OpenAI Service"
            if x == "azure_openai"
            else "OpenAI Platform API",
            index=0 if st.session_state.config.provider == "azure_openai" else 1,
        )

        deployment_model = st.selectbox(
            "Deployment / Model",
            options=["gpt-4-1106-preview", "gpt-4", "gpt-35-turbo"],
            index=0,
        )

        persona = st.selectbox(
            "System Persona",
            options=list(PERSONA_PRESETS.keys()),
            index=0,
        )

        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.config.temperature,
            step=0.05,
        )

        max_tokens = st.slider(
            "Max Output Tokens",
            min_value=256,
            max_value=4096,
            value=st.session_state.config.max_tokens,
            step=256,
        )

        st.session_state.config.provider = provider
        st.session_state.config.azure_openai_deployment = deployment_model
        st.session_state.config.openai_model_name = deployment_model
        st.session_state.config.temperature = temperature
        st.session_state.config.max_tokens = max_tokens
        st.session_state.config.default_persona = persona

        st.divider()
        is_live, status_msg = st.session_state.chatbot.is_live_mode, st.session_state.chatbot.status_message
        if is_live:
            st.success(f"🟢 {status_msg}")
        else:
            st.info(f"🔵 {status_msg}")

        st.caption(f"Session ID: `{st.session_state.session_id}`")

        if st.button("🗑️ Clear Conversation History", use_container_width=True):
            st.session_state.chatbot.clear_session(st.session_state.session_id)
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "Conversation memory cleared. How can I assist you today?",
                }
            ]
            st.rerun()

    st.header("OpenAI LLM Conversational Chatbot")
    st.markdown(
        f"**Active Persona:** `{persona}` &nbsp;|&nbsp; "
        f"**Deployment:** `{deployment_model}` &nbsp;|&nbsp; "
        f"**Temperature:** `{temperature}`"
    )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_prompt := st.chat_input("Ask a technical or architectural question..."):
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            accumulated_response = ""
            for token in st.session_state.chatbot.stream_chat(
                user_input=user_prompt,
                session_id=st.session_state.session_id,
                persona_name=persona,
            ):
                accumulated_response += token
                response_placeholder.markdown(accumulated_response + "▌")
            response_placeholder.markdown(accumulated_response)

        st.session_state.messages.append(
            {"role": "assistant", "content": accumulated_response}
        )


if __name__ == "__main__":
    main()

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
##
# Description:-
#
#       Command-line interface (CLI) for interacting with the Azure OpenAI
#       & LangChain conversational chatbot directly from a terminal session.
#
##
# Development date    Developed by       Comments
# ----------------    ------------       ---------
# 04/11/2023          Saddam Khan        Initial implementation
# 22/11/2023          Saddam Khan        Added interactive session loop and clear command
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import sys
from config import ChatbotConfig
from chatbot import OpenAILLMChatbot


def run_cli() -> None:
    """Start interactive CLI chat loop."""
    config = ChatbotConfig()
    chatbot = OpenAILLMChatbot(config)
    session_id = "cli-session-01"

    print("=" * 72)
    print("  Azure OpenAI & LangChain Conversational Chatbot CLI")
    print(f"  Provider: {config.provider} | Deployment: {config.azure_openai_deployment}")
    print(f"  Status:   {chatbot.status_message}")
    print("  Commands: '/clear' to reset memory, '/exit' or '/quit' to quit")
    print("=" * 72)

    while True:
        try:
            user_input = input("\nYou > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting chatbot CLI.")
            sys.exit(0)

        if not user_input:
            continue
        if user_input.lower() in {"/exit", "/quit", "exit", "quit"}:
            print("Goodbye!")
            break
        if user_input.lower() == "/clear":
            chatbot.clear_session(session_id)
            print("[Session history cleared]")
            continue

        print("\nAssistant > ", end="", flush=True)
        for chunk in chatbot.stream_chat(user_input, session_id=session_id):
            print(chunk, end="", flush=True)
        print()


if __name__ == "__main__":
    run_cli()

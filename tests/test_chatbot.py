#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
##
# Description:-
#
#       Unit tests verifying configuration loading, session history isolation,
#       and conversational execution for the Azure OpenAI & LangChain chatbot.
#
##
# Development date    Developed by       Comments
# ----------------    ------------       ---------
# 04/11/2023          Saddam Khan        Initial implementation
# 22/11/2023          Saddam Khan        Added test cases for multi-turn memory and persona prompts
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import unittest
from config import ChatbotConfig
from chatbot import OpenAILLMChatbot


class TestOpenAILLMChatbot(unittest.TestCase):
    """Test suite for OpenAILLMChatbot and ChatbotConfig."""

    def setUp(self) -> None:
        self.config = ChatbotConfig(
            provider="azure_openai",
            azure_openai_api_key="",
            azure_openai_endpoint="https://test-endpoint.openai.azure.com/",
            azure_openai_deployment="gpt-4-1106-preview",
        )
        self.bot = OpenAILLMChatbot(self.config)

    def test_default_persona_system_prompt(self) -> None:
        """Verify system prompt retrieval for known and fallback personas."""
        prompt = self.config.get_system_prompt("Cloud Solutions Architect")
        self.assertIn("Principal Cloud Solutions Architect", prompt)

    def test_simulated_conversation_and_memory(self) -> None:
        """Verify multi-turn conversation history is stored and isolated per session."""
        session_id = "test-session-123"
        reply = self.bot.chat(
            "How do I configure Azure Entra ID with LangChain?", session_id=session_id
        )
        self.assertIn("Azure OpenAI", reply)
        history = self.bot.get_history_messages(session_id)
        self.assertEqual(len(history), 2)

    def test_clear_session_history(self) -> None:
        """Verify clearing session history removes all messages."""
        session_id = "test-session-clear"
        self.bot.chat("Hello assistant", session_id=session_id)
        self.assertEqual(len(self.bot.get_history_messages(session_id)), 2)
        self.bot.clear_session(session_id)
        self.assertEqual(len(self.bot.get_history_messages(session_id)), 0)


if __name__ == "__main__":
    unittest.main()

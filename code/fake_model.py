"""A scripted chat model for learning and for unit tests - no API key, no cost.

GenericFakeChatModel replays the messages you give it, in order. It has no
bind_tools(), so we add one that does nothing. This is the pattern the LangChain
testing docs recommend.

Set REAL_MODEL=1 (and ANTHROPIC_API_KEY) to use Claude instead of the script.
"""
import os

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel


class FakeToolCallingModel(GenericFakeChatModel):
    def bind_tools(self, tools, **kwargs):  # the fake model ignores the tool list
        return self


def get_model(script):
    """Return Claude when REAL_MODEL=1, else a fake model that replays `script`."""
    if os.environ.get("REAL_MODEL") == "1":
        from langchain.chat_models import init_chat_model
        # Note: Claude Sonnet 5.5 rejects temperature, top_p and top_k. Leave them out.
        return init_chat_model("anthropic:claude-sonnet-5-5")
    return FakeToolCallingModel(messages=iter(script))

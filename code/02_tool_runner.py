"""Module 2 - the same agent, with the SDK's tool runner (beta) driving the loop.

Run:
    export ANTHROPIC_API_KEY=...
    python 02_tool_runner.py

You write only the tool functions. The type hints and the docstring become the
tool's input schema and description. Write the loop yourself first (01_agent_loop.py)
so you know what this helper does for you.
"""
from datetime import datetime, timezone

import anthropic
from anthropic import beta_tool

client = anthropic.Anthropic()


@beta_tool
def time_now() -> str:
    """Return the current date and time in UTC (ISO 8601)."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@beta_tool
def add(a: int, b: int) -> str:
    """Add two integers exactly.

    Args:
        a: The first number.
        b: The second number.
    """
    return str(a + b)


runner = client.beta.messages.tool_runner(
    model="claude-opus-5-5",
    max_tokens=16000,
    max_iterations=10,  # the step limit
    tools=[time_now, add],
    messages=[{"role": "user", "content": "What is 1234 plus 5678, and what time is it?"}],
)

for message in runner:            # one item per model call
    print("stop_reason:", message.stop_reason)

final = runner.until_done()
print("".join(b.text for b in final.content if b.type == "text"))

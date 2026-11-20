"""Module 2 - the whole agent loop, with no framework.

Run:
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=...        # from console.anthropic.com
    python 01_agent_loop.py

Every agent framework hides a loop like this one. Read it line by line.
"""
from datetime import datetime, timezone

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
MODEL = "claude-opus-5-5"       # claude-sonnet-5-5 or claude-haiku-5-5 cost less
SYSTEM = "You are a brief, careful assistant. Use a tool when it gives a better answer."

TOOLS = [
    {
        "name": "time_now",
        "description": "Return the current date and time in UTC (ISO 8601). "
                       "Use it for any question about today's date or the time.",
        "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "add",
        "description": "Add two integers exactly. Use it instead of doing sums in your head.",
        "input_schema": {
            "type": "object",
            "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
            "required": ["a", "b"],
            "additionalProperties": False,
        },
    },
]


def run_tool(name: str, args: dict) -> str:
    """Your code runs the tools. The model only asks."""
    if name == "time_now":
        return datetime.now(timezone.utc).isoformat(timespec="seconds")
    if name == "add":
        return str(args["a"] + args["b"])
    raise ValueError(f"unknown tool {name!r}")


def agent(task: str, max_steps: int = 10) -> str:
    messages = [{"role": "user", "content": task}]
    for _ in range(max_steps):                                   # limit: steps
        reply = client.messages.create(
            model=MODEL, max_tokens=16000,
            system=SYSTEM, tools=TOOLS, messages=messages,
        )
        messages.append({"role": "assistant", "content": reply.content})  # the whole reply

        if reply.stop_reason == "refusal":                       # the model declined
            return "The model declined this request."
        if reply.stop_reason == "max_tokens":                    # never run a cut-off call
            return "I stopped: my reply was too long."
        if reply.stop_reason != "tool_use":                      # "end_turn": done
            return "".join(b.text for b in reply.content if b.type == "text")

        results = []
        for block in reply.content:
            if block.type != "tool_use":
                continue
            try:
                out, failed = run_tool(block.name, block.input), False
            except Exception as e:                               # errors go back to the model
                out, failed = f"Tool error: {e}", True
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,                         # links result to request
                "content": out,
                "is_error": failed,
            })
        messages.append({"role": "user", "content": results})    # all results, one message
    return "I stopped: I reached my step limit."


if __name__ == "__main__":
    print(agent("What is 1234 plus 5678, and what time is it?"))

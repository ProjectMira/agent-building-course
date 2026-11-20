"""Module 8 - human approval with LangChain's HumanInTheLoopMiddleware.

The middleware pauses before chosen tools. You resume with one decision per
pending action: approve, edit, reject or respond.
Runs with a fake model:  python 06_hitl_middleware.py
"""
import json

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.messages import AIMessage, ToolCall
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from fake_model import get_model


@tool
def add(a: int, b: int) -> int:
    """Add two integers exactly."""
    return a + b


@tool
def delete_file(path: str) -> str:
    """Delete a file. This cannot be undone."""
    print(f"    !!! delete_file really ran on {path}")
    return f"deleted {path}"


def make_agent():
    model = get_model([
        AIMessage(content="", tool_calls=[ToolCall(name="delete_file", args={"path": "report.pdf"}, id="call_1")]),
        AIMessage(content="Done."),
    ])
    return create_agent(
        model, tools=[add, delete_file],
        middleware=[HumanInTheLoopMiddleware(interrupt_on={
            "delete_file": {"allowed_decisions": ["approve", "edit", "reject"]},  # ask first
            "add": False,                                                         # never ask
        })],
        checkpointer=InMemorySaver(),
    )


user = {"messages": [{"role": "user", "content": "Delete report.pdf"}]}
for decision in ({"type": "approve"}, {"type": "reject", "message": "Keep the report."}):
    agent = make_agent()
    config = {"configurable": {"thread_id": f"hitl-{decision['type']}"}}
    print(f"=== the person chooses: {decision['type']} ===")
    paused = agent.invoke(user, config)
    print("  the card shows:", json.dumps(paused["__interrupt__"][0].value["action_requests"][0]["args"]))
    result = agent.invoke(Command(resume={"decisions": [decision]}), config)
    tool_msg = [m for m in result["messages"] if type(m).__name__ == "ToolMessage"][0]
    print(f"  tool result: {tool_msg.content!r} (status={tool_msg.status})")

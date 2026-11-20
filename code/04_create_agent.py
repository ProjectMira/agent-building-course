"""Module 8 - the same agent in four lines with LangChain v1's create_agent.

create_agent builds the model/tools graph of 03_langgraph_loop.py for you.
Runs with a fake model:      python 04_create_agent.py
Runs with Claude:            REAL_MODEL=1 ANTHROPIC_API_KEY=... python 04_create_agent.py
"""
from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware, ToolCallLimitMiddleware
from langchain.messages import AIMessage, ToolCall
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

from fake_model import get_model


@tool
def add(a: int, b: int) -> int:
    """Add two integers exactly."""
    return a + b


model = get_model([
    AIMessage(content="", tool_calls=[ToolCall(name="add", args={"a": 1234, "b": 5678}, id="call_1")]),
    AIMessage(content="1234 + 5678 = 6912."),
])

agent = create_agent(
    model,                                   # or the string "anthropic:claude-sonnet-5-5"
    tools=[add],
    system_prompt="You are a careful calculator. Use the add tool for every sum.",
    middleware=[
        ModelCallLimitMiddleware(run_limit=10),   # step limit (Module 2)
        ToolCallLimitMiddleware(run_limit=20),
    ],
    checkpointer=InMemorySaver(),
)

print("nodes:", list(agent.get_graph().nodes))      # the same graph as before
result = agent.invoke({"messages": [{"role": "user", "content": "What is 1234 + 5678?"}]},
                      {"configurable": {"thread_id": "lesson-8"}})
for m in result["messages"]:
    print(f"{type(m).__name__:12} {m.content!r} {getattr(m, 'tool_calls', '') or ''}")

"""Module 6 - the agent loop of Module 2, as a LangGraph graph.

Two nodes (model, tools), one conditional edge, a checkpointer and a thread id.
Runs with a fake model:      python 03_langgraph_loop.py
Runs with Claude:            REAL_MODEL=1 ANTHROPIC_API_KEY=... python 03_langgraph_loop.py
"""
from typing import Annotated

from typing_extensions import TypedDict
from langchain.messages import AIMessage, AnyMessage, ToolCall
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from fake_model import get_model


@tool
def add(a: int, b: int) -> int:
    """Add two integers exactly."""
    return a + b


# 1. State: the data that travels through the graph.
#    add_messages is a reducer: new messages are APPENDED, not overwritten.
class State(TypedDict):          # the same as: from langgraph.graph import MessagesState
    messages: Annotated[list[AnyMessage], add_messages]


model = get_model([               # what the fake model will "say", in order
    AIMessage(content="", tool_calls=[ToolCall(name="add", args={"a": 1234, "b": 5678}, id="call_1")]),
    AIMessage(content="1234 + 5678 = 6912."),
    AIMessage(content="You asked me to add 1234 and 5678."),
]).bind_tools([add])


# 2. Nodes: plain functions. They get the state and return only the UPDATE.
def call_model(state: State):
    return {"messages": [model.invoke(state["messages"])]}


# 3. Edges: START -> model; model -> tools or END; tools -> model.
builder = StateGraph(State)
builder.add_node("model", call_model)
builder.add_node("tools", ToolNode([add]))          # runs every tool call in the last message
builder.add_edge(START, "model")
builder.add_conditional_edges("model", tools_condition, {"tools": "tools", END: END})
builder.add_edge("tools", "model")

# 4. Compile with a checkpointer: the state is saved after every step.
graph = builder.compile(checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "lesson-6"}}  # the "save slot"

print("--- turn 1: watch each node's update ---")
for update in graph.stream({"messages": [{"role": "user", "content": "What is 1234 + 5678?"}]},
                           config, stream_mode="updates"):
    for node, delta in update.items():
        m = delta["messages"][-1]
        print(f"[{node:5}] {type(m).__name__}: {m.content!r} {getattr(m, 'tool_calls', '') or ''}")

print("--- turn 2: same thread_id, so the graph remembers turn 1 ---")
out = graph.invoke({"messages": [{"role": "user", "content": "What did I ask you?"}]}, config)
print("answer:", out["messages"][-1].content)
print("messages in this thread:", len(out["messages"]))
print("checkpoints saved:", len(list(graph.get_state_history(config))))

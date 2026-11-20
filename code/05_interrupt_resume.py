"""Module 7 - pause for a person with interrupt(), then resume with Command(resume=...).

Watch the line "node starts" print TWICE: on resume, LangGraph runs the paused
node again from its first line. Anything before interrupt() happens again.
No model and no key needed:  python 05_interrupt_resume.py
"""
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

sent = []                      # stands in for an email server


class State(TypedDict):
    draft: str
    status: str


def notify_bad(state: State):
    print("  > node starts")
    sent.append(state["draft"])                        # side effect BEFORE the pause
    ok = interrupt({"question": "Also post this in #news?", "draft": state["draft"]})
    return {"status": "posted" if ok else "email only"}


def notify_good(state: State):
    print("  > node starts")
    ok = interrupt({"question": "Send the email and post in #news?", "draft": state["draft"]})
    if ok:                                              # act only AFTER the last decision
        sent.append(state["draft"])
    return {"status": "sent and posted" if ok else "cancelled"}


def build(node):
    g = StateGraph(State)
    g.add_node("notify", node)
    g.add_edge(START, "notify")
    g.add_edge("notify", END)
    return g.compile(checkpointer=InMemorySaver())    # interrupt() needs a checkpointer


for name, node in [("act, then ask", notify_bad), ("ask first, then act", notify_good)]:
    sent.clear()
    graph = build(node)
    config = {"configurable": {"thread_id": name}}
    print(f"=== {name} ===")
    paused = graph.invoke({"draft": "Our new course is live!", "status": ""}, config)
    print("  paused, waiting for:", paused["__interrupt__"][0].value["question"])
    print("  next node:", graph.get_state(config).next)
    # ... hours later, maybe after a restart. Only the checkpoint is needed.
    done = graph.invoke(Command(resume=True), config)   # the person says yes
    print("  status:", done["status"], "| emails sent:", len(sent))

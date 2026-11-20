"""Module 10 - the parallel pattern in LangGraph: fan out with Send, merge with a reducer.

One node splits a job; Send starts one worker per item, in parallel; a reducer
(operator.add) merges the workers' results; one node writes the summary.
No model and no key needed:  python 07_send_map_reduce.py
"""
import operator
from typing import Annotated

from typing_extensions import TypedDict
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send


class State(TypedDict):
    documents: list[str]
    summaries: Annotated[list[str], operator.add]   # parallel writes are ADDED together
    report: str


class WorkerState(TypedDict):
    doc: str


def fan_out(state: State):
    # One Send per document. Each runs the "summarise" node with its own small input.
    return [Send("summarise", {"doc": d}) for d in state["documents"]]


def summarise(state: WorkerState):
    # A real agent would call a model here.
    return {"summaries": [f"{state['doc']}: {len(state['doc'].split())} words"]}


def combine(state: State):
    return {"report": " | ".join(sorted(state["summaries"]))}


g = StateGraph(State)
g.add_node("summarise", summarise)
g.add_node("combine", combine)
g.add_conditional_edges(START, fan_out, ["summarise"])
g.add_edge("summarise", "combine")
g.add_edge("combine", END)
graph = g.compile()

out = graph.invoke({"documents": ["leave policy for volunteers", "travel rules", "how to book a room"],
                    "summaries": [], "report": ""})
print(out["report"])

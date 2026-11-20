# Agent Building Course

A free, hands-on course on building AI agents and agentic systems.

**Read it here: https://projectmira.github.io/agent-building-course/**

From one 50-line agent loop to durable, safe, tested agents in LangGraph, and a look inside a real agent system in daily use.

- **Part 1 · Foundations:** what an agent is, the agent loop, tools and MCP, context engineering, memory and knowledge.
- **Part 2 · LangGraph & LangChain:** state, nodes and edges; checkpoints, `interrupt()` and resume; `create_agent` and middleware; choosing a framework.
- **Part 3 · Production systems:** workflow patterns, proactive agents, multi-agent systems, security, evals, cost, shipping, and a capstone project.
- **Part 4 · How we built ours:** a case study of a team of job agents, and what changed after real use.

Every module has a short story, plain-English analogies, worked examples, quizzes, and a "Try it" task. Six labs in the page simulate the loop, a graph run, context packing, interrupt replay, the lethal trifecta and task cost.

## Code

The [`code/`](code/) folder has small programs that go with the modules. The LangGraph and LangChain examples run with a fake model, so they are free. See [`code/README.md`](code/README.md).

## How it is built

One static page (`index.html`) with `assets/course.css` and `assets/course.js`. No build step. Progress and XP are kept in your browser's local storage only.

To run it locally:

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

Facts, prices, package versions and links were checked on 21 November 2026. Agent tooling changes fast: if something here is out of date, please open an issue.

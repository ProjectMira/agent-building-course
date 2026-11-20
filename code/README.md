# Course code

Small programs that go with the [Agent Building Course](https://projectmira.github.io/agent-building-course/).
Each file is one idea. Read it top to bottom, run it, then change one thing and run it again.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

| File | Module | Needs a key? | What it shows |
|---|---|---|---|
| `01_agent_loop.py` | 2 | Yes (`ANTHROPIC_API_KEY`) | The whole agent loop with the Anthropic SDK, no framework |
| `02_tool_runner.py` | 2 | Yes | The same agent with the SDK's tool runner (beta) |
| `03_langgraph_loop.py` | 6 | No | The loop as a LangGraph graph: state, nodes, edges, checkpointer, thread |
| `04_create_agent.py` | 8 | No | The same agent with LangChain v1 `create_agent` and limit middleware |
| `05_interrupt_resume.py` | 7 | No | `interrupt()` and `Command(resume=...)`, and why the paused node runs twice |
| `06_hitl_middleware.py` | 8 | No | Approve or reject a tool call with `HumanInTheLoopMiddleware` |
| `07_send_map_reduce.py` | 10 | No | The parallel pattern: fan out with `Send`, merge with a reducer |

Files 03 to 06 use a scripted fake model (`fake_model.py`), so they are free and give the same output every time.
To use Claude instead:

```bash
export ANTHROPIC_API_KEY=...
REAL_MODEL=1 python 03_langgraph_loop.py
```

With a real model the answers change from run to run. That is normal, and it is why Module 14 is about evals.

Tested with: anthropic 2.12.0, langgraph 1.2.24, langchain 1.5.2, langchain-core 1.8.4, langchain-anthropic 1.7.12.

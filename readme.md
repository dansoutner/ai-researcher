# AI researcher PoC

## Requirements
- Python 3.10+
- Together API key (`TOGETHER_API_KEY`)

## Installation
If you're using `uv` or `pip`, install dependencies from `pyproject.toml`.

## Run
### LangGraph (agent_v2)
This repo includes a LangGraph rewrite of the Together ReAct data science agent.

- Module:
  - `python -m agent_v2.langgraph_agent --query "..."`
- Script entrypoint (when installed):
  - `ai-researcher-agent-v2 --query "..."`

Common flags:
- `--data-dir ./data` to upload local files to the Together code interpreter session
- `--model <together-model-name>`
- `--max-iterations 15`

## MCP servers
TODO
brew install uv
https://glama.ai/mcp/servers/@lecigarevolant/arxiv-mcp-server-gpt
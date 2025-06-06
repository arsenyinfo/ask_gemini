# ask-gemini

A minimal MCP server that exposes Google's Gemini 2.5 Flash with web search capabilities as a tool.

- Provides access to Gemini 2.5 Flash
- Includes built-in Google Search integration for up-to-date information.

Currently Google provides [1500 search queries per day for free](https://ai.google.dev/gemini-api/docs/grounding?lang=python#configure-search).

## Prerequisites

- [uv package manager](https://docs.astral.sh/uv/)
- Gemini API key in your environment variable `GEMINI_API_KEY`

## Installation

```bash
uv sync
```

## Usage

Set your Gemini API key:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

Run as MCP server:
```bash
uv run python main.py
```

Attach to Claude Code
```bash
claude mcp add --transport sse "search" http://127.0.0.1:8000/mcp
```
Of course, other MCP clients can use it too.

## Reliability

Gemini API is known for being not the most reliable, PRs with retries and other workarounds are welcome. 

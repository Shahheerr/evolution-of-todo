---
name: OpenAI Agents SDK
description: Complete reference for building AI agents using the official OpenAI Agents SDK for Python
---

# OpenAI Agents SDK

The OpenAI Agents SDK (`openai-agents`) is a lightweight Python library for building agentic AI applications. It provides primitives for creating agents with tools, handoffs, guardrails, and tracing.

## Package Information

- **Package Name**: `openai-agents`
- **PyPI**: https://pypi.org/project/openai-agents/
- **GitHub**: https://github.com/openai/openai-agents-python
- **Documentation**: https://openai.github.io/openai-agents-python/

## Installation

```bash
# Using pip
pip install openai-agents

# Using uv
uv add openai-agents
```

## Core Concepts

### 1. Agent
An Agent is an LLM configured with instructions, tools, and behaviors. Agents can call tools, hand off to other agents, and produce structured outputs.

### 2. Runner
The Runner executes agents in a loop, handling tool calls and handoffs until a final response is produced.

### 3. Tools
Tools are functions that agents can call. They use Python type hints and docstrings to define their schema.

### 4. Handoffs
Handoffs allow agents to transfer control to other agents, enabling multi-agent workflows.

### 5. Guardrails
Guardrails validate agent inputs/outputs and can interrupt execution.

### 6. Tracing
Built-in tracing tracks agent execution for debugging and monitoring.

## File Structure Reference

See the following files for detailed implementation:

- `agents/` - Agent implementation patterns
  - `basic-agent.md` - Creating and running agents
  - `tools.md` - Defining agent tools
  - `handoffs.md` - Multi-agent handoffs
  - `context.md` - Using context variables

- `runners/` - Runner patterns
  - `runner.md` - Running agents
  - `streaming.md` - Streaming responses

- `advanced/` - Advanced features
  - `guardrails.md` - Input/output validation
  - `tracing.md` - Execution tracing
  - `models.md` - Model configuration

- `examples/` - Complete examples
  - `customer-service.md` - Multi-agent customer service
  - `research-assistant.md` - Research with tools

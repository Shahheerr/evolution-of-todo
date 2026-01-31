---
name: OpenAI ChatKit
description: Complete reference for building chat interfaces using the OpenAI ChatKit SDK
---

# OpenAI ChatKit

ChatKit is OpenAI's SDK for building chat UIs with real-time streaming, function calling, and assistants. It provides both backend (Python) and frontend (React) libraries.

## Package Information

### Backend (Python)

- **Package Name**: `chatkit`
- **PyPI**: https://pypi.org/project/chatkit/
- **Documentation**: https://platform.openai.com/docs/guides/chatkit

### Frontend (React)

- **Package Name**: `@openai/chatkit-react`
- **npm**: https://www.npmjs.com/package/@openai/chatkit-react
- **Documentation**: https://platform.openai.com/docs/guides/chatkit

## Installation

### Backend

```bash
# Using pip
pip install chatkit

# Using uv
uv add chatkit
```

### Frontend

```bash
# Using npm
npm install @openai/chatkit-react

# Using pnpm
pnpm add @openai/chatkit-react
```

## Core Concepts

### 1. ChatKit Server
The backend server handles AI interactions, tool execution, and state management.

### 2. ChatKit Client
The frontend components render the chat UI and handle real-time streaming.

### 3. Tools
Functions the AI can call, defined with JSON schema.

### 4. Streaming
Real-time response streaming using Server-Sent Events (SSE).

### 5. Messages
Conversation history with user, assistant, and tool messages.

## File Structure Reference

See the following files for detailed implementation:

- `backend/` - Python backend implementation
  - `server.md` - ChatKit server setup
  - `tools.md` - Defining and executing tools
  - `state.md` - State management
  - `streaming.md` - SSE streaming

- `frontend/` - React frontend implementation
  - `client.md` - ChatKit React client
  - `components.md` - Built-in UI components
  - `hooks.md` - React hooks
  - `customization.md` - Styling and customization

- `integration/` - Full-stack integration
  - `fastapi.md` - Integration with FastAPI
  - `nextjs.md` - Integration with Next.js

- `examples/` - Complete examples
  - `chat-assistant.md` - Basic chat assistant
  - `tool-calling.md` - Agent with tools

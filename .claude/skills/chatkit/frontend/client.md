# ChatKit React Client

The React client for building chat UIs with streaming support.

## Installation

```bash
npm install @openai/chatkit-react
```

## Basic Usage

```tsx
import { ChatKitProvider, Chat } from '@openai/chatkit-react';

function App() {
    return (
        <ChatKitProvider url="http://localhost:8000/chatkit">
            <Chat />
        </ChatKitProvider>
    );
}
```

## Provider Configuration

```tsx
import { ChatKitProvider } from '@openai/chatkit-react';

function App() {
    return (
        <ChatKitProvider
            url="http://localhost:8000/chatkit"
            
            // Authentication
            getAuthToken={async () => {
                const token = await fetchToken();
                return token;
            }}
            
            // Initial messages
            initialMessages={[
                { role: "assistant", content: "Hello! How can I help?" }
            ]}
            
            // Context for backend
            context={{
                user_id: "123",
                session_id: "abc"
            }}
            
            // Error handling
            onError={(error) => {
                console.error("ChatKit error:", error);
            }}
        >
            <Chat />
        </ChatKitProvider>
    );
}
```

## Chat Component

```tsx
import { Chat } from '@openai/chatkit-react';

// Basic usage
<Chat />

// With props
<Chat
    placeholder="Type your message..."
    submitLabel="Send"
    className="my-chat"
    
    // Callbacks
    onMessageSend={(message) => {
        console.log("Sent:", message);
    }}
    onResponse={(response) => {
        console.log("Response:", response);
    }}
/>
```

## Custom Chat UI

```tsx
import { useChat, useChatMessages, useChatInput } from '@openai/chatkit-react';

function CustomChat() {
    const { messages, isLoading, error } = useChatMessages();
    const { input, setInput, submit } = useChatInput();
    
    return (
        <div className="chat-container">
            {/* Messages */}
            <div className="messages">
                {messages.map((msg, i) => (
                    <div key={i} className={`message ${msg.role}`}>
                        {msg.content}
                    </div>
                ))}
                
                {isLoading && <div className="loading">Thinking...</div>}
                {error && <div className="error">{error.message}</div>}
            </div>
            
            {/* Input */}
            <form onSubmit={(e) => { e.preventDefault(); submit(); }}>
                <input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type a message..."
                    disabled={isLoading}
                />
                <button type="submit" disabled={isLoading || !input.trim()}>
                    Send
                </button>
            </form>
        </div>
    );
}

function App() {
    return (
        <ChatKitProvider url="http://localhost:8000/chatkit">
            <CustomChat />
        </ChatKitProvider>
    );
}
```

## Hooks Reference

### useChat

```tsx
import { useChat } from '@openai/chatkit-react';

function Component() {
    const {
        // State
        messages,       // Message[]
        isLoading,      // boolean
        error,          // Error | null
        
        // Actions
        sendMessage,    // (content: string) => Promise<void>
        clearMessages,  // () => void
        retry,          // () => Promise<void>
    } = useChat();
}
```

### useChatMessages

```tsx
import { useChatMessages } from '@openai/chatkit-react';

function Messages() {
    const { messages, isLoading, error } = useChatMessages();
    
    return (
        <div>
            {messages.map((msg, i) => (
                <div key={i}>{msg.content}</div>
            ))}
        </div>
    );
}
```

### useChatInput

```tsx
import { useChatInput } from '@openai/chatkit-react';

function Input() {
    const { input, setInput, submit, isSubmitting } = useChatInput();
    
    return (
        <form onSubmit={(e) => { e.preventDefault(); submit(); }}>
            <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
            />
            <button disabled={isSubmitting}>Send</button>
        </form>
    );
}
```

### useChatStream

```tsx
import { useChatStream } from '@openai/chatkit-react';

function Component() {
    const { streamingContent, isStreaming } = useChatStream();
    
    return (
        <div>
            {isStreaming && <span>{streamingContent}</span>}
        </div>
    );
}
```

## Message Types

```typescript
interface Message {
    role: "user" | "assistant" | "tool";
    content: string;
    id?: string;
    timestamp?: Date;
    toolCalls?: ToolCall[];
}

interface ToolCall {
    id: string;
    name: string;
    arguments: Record<string, unknown>;
    result?: string;
}
```

## Error Handling

```tsx
import { ChatKitProvider, useChat } from '@openai/chatkit-react';

function ChatWithErrors() {
    const { messages, error, retry } = useChat();
    
    return (
        <div>
            {messages.map((msg, i) => (
                <div key={i}>{msg.content}</div>
            ))}
            
            {error && (
                <div className="error">
                    <p>{error.message}</p>
                    <button onClick={retry}>Retry</button>
                </div>
            )}
        </div>
    );
}

function App() {
    return (
        <ChatKitProvider
            url="http://localhost:8000/chatkit"
            onError={(error) => {
                // Log to monitoring service
                logError(error);
            }}
        >
            <ChatWithErrors />
        </ChatKitProvider>
    );
}
```

## Styling

```tsx
import { Chat } from '@openai/chatkit-react';

// Using className
<Chat className="my-chat" />

// Using classNames object
<Chat
    classNames={{
        container: "chat-container",
        messages: "chat-messages",
        input: "chat-input",
        button: "chat-button",
        userMessage: "user-message",
        assistantMessage: "assistant-message"
    }}
/>
```

## Complete Example

```tsx
"use client";

import React from 'react';
import {
    ChatKitProvider,
    useChat,
    useChatMessages,
    useChatInput,
    useChatStream
} from '@openai/chatkit-react';

function ChatUI() {
    const { isLoading, error, clearMessages } = useChat();
    const { messages } = useChatMessages();
    const { input, setInput, submit } = useChatInput();
    const { streamingContent, isStreaming } = useChatStream();
    
    const messagesEndRef = React.useRef<HTMLDivElement>(null);
    
    // Auto-scroll
    React.useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, streamingContent]);
    
    return (
        <div className="chat-container">
            {/* Header */}
            <div className="chat-header">
                <h2>AI Assistant</h2>
                <button onClick={clearMessages}>Clear</button>
            </div>
            
            {/* Messages */}
            <div className="chat-messages">
                {messages.map((msg, i) => (
                    <div key={i} className={`message ${msg.role}`}>
                        <div className="message-content">
                            {msg.content}
                        </div>
                    </div>
                ))}
                
                {/* Streaming indicator */}
                {isStreaming && (
                    <div className="message assistant streaming">
                        {streamingContent}
                        <span className="cursor">▊</span>
                    </div>
                )}
                
                {/* Loading indicator */}
                {isLoading && !isStreaming && (
                    <div className="loading">
                        <span className="dot"></span>
                        <span className="dot"></span>
                        <span className="dot"></span>
                    </div>
                )}
                
                {/* Error */}
                {error && (
                    <div className="error">
                        ⚠️ {error.message}
                    </div>
                )}
                
                <div ref={messagesEndRef} />
            </div>
            
            {/* Input */}
            <form
                className="chat-input"
                onSubmit={(e) => {
                    e.preventDefault();
                    if (input.trim() && !isLoading) {
                        submit();
                    }
                }}
            >
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type a message..."
                    disabled={isLoading}
                />
                <button
                    type="submit"
                    disabled={isLoading || !input.trim()}
                >
                    Send
                </button>
            </form>
        </div>
    );
}

export function ChatWidget() {
    const getAuthToken = async () => {
        // Get JWT from your auth system
        const response = await fetch('/api/auth/token');
        const { token } = await response.json();
        return token;
    };
    
    return (
        <ChatKitProvider
            url={process.env.NEXT_PUBLIC_CHATKIT_URL || "http://localhost:8000/chatkit"}
            getAuthToken={getAuthToken}
            initialMessages={[
                {
                    role: "assistant",
                    content: "Hello! I'm your AI assistant. How can I help you today?"
                }
            ]}
            onError={(error) => {
                console.error("ChatKit error:", error);
            }}
        >
            <ChatUI />
        </ChatKitProvider>
    );
}
```

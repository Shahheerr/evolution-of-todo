"use client";

/**
 * AI Chat Component
 *
 * AI-powered chat interface for task management with SSE streaming.
 */

import { useEffect, useRef, useState, useCallback } from "react";
import { sendChatMessage, formatMessage, type ChatMessage } from "@/lib/chat-api";

interface AIChatProps {
  onTasksUpdated?: () => void;
}

export function AIChat({ onTasksUpdated }: AIChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content: `👋 Hi! I'm your TaskFlow AI assistant.

I can help you manage your tasks through conversation. Try:
- **"Add a task to buy groceries"**
- **"Show my tasks"**
- **"Mark groceries as done"**
- **"Delete the groceries task"**

What would you like to do?`,
      timestamp: new Date(),
    }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = useCallback(async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    setError(null);

    // Create placeholder for assistant response
    const assistantId = `assistant-${Date.now()}`;
    setMessages((prev) => [...prev, {
      id: assistantId,
      role: "assistant",
      content: "",
      timestamp: new Date(),
    }]);

    try {
      const newSessionId = await sendChatMessage(
        userMessage.content,
        sessionId,
        (event) => {
          if (event.type === "content") {
            setMessages((prev) => {
              const updated = prev.map((msg) =>
                msg.id === assistantId
                  ? { ...msg, content: msg.content + event.content }
                  : msg
              );
              return updated;
            });
          } else if (event.type === "tool_call") {
            console.log("Tool called:", event.tool_call);
          } else if (event.type === "error") {
            setError(event.error);
          } else if (event.type === "done") {
            setIsLoading(false);
            onTasksUpdated?.();
          }
        }
      );

      setSessionId(newSessionId);
    } catch (err) {
      console.error("AI Chat error:", err);
      const errorMessage = err instanceof Error ? err.message : "An error occurred";

      setError(errorMessage);
      setMessages((prev) => [...prev, {
        id: `error-${Date.now()}`,
        role: "assistant",
        content: `❌ ${errorMessage}

Please make sure the backend server is running and you have configured your OpenAI API key.`,
        timestamp: new Date(),
      }]);
    } finally {
      setIsLoading(false);
    }
  }, [input, isLoading, sessionId, onTasksUpdated]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="ai-chat-container">
      {/* Header */}
      <div className="ai-chat-header">
        <div className="ai-chat-title">
          <span className="ai-chat-icon">🤖</span>
          <span>TaskFlow AI</span>
        </div>
        <span className="ai-chat-status">
          {isLoading ? "Thinking..." : "Online"}
        </span>
      </div>

      {/* Messages */}
      <div className="ai-chat-messages">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`ai-chat-message ${msg.role === "user" ? "user" : "assistant"}`}
          >
            <div className="ai-chat-message-avatar">
              {msg.role === "user" ? "👤" : "🤖"}
            </div>
            <div className="ai-chat-message-content">
              <div
                className="ai-chat-message-text"
                dangerouslySetInnerHTML={{
                  __html: formatMessage(msg.content)
                }}
              />
              <div className="ai-chat-message-time">
                {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
        ))}

        {isLoading && messages[messages.length - 1]?.role === "user" && (
          <div className="ai-chat-message assistant">
            <div className="ai-chat-message-avatar">🤖</div>
            <div className="ai-chat-message-content">
              <div className="ai-chat-typing">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Error Banner */}
      {error && (
        <div className="ai-chat-error">
          <span>⚠️ {error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {/* Input */}
      <div className="ai-chat-input-container">
        <input
          type="text"
          className="ai-chat-input"
          placeholder="Ask me to manage your tasks..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
        />
        <button
          className="ai-chat-send-btn"
          onClick={sendMessage}
          disabled={isLoading || !input.trim()}
        >
          {isLoading ? "..." : "→"}
        </button>
      </div>
    </div>
  );
}

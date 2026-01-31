"use client";

/**
 * AI Chat Component
 * 
 * This component provides an AI-powered chat interface for task management.
 * Users can add, list, update, delete, and complete tasks through natural conversation.
 */

import { useEffect, useRef, useState, useCallback } from "react";
import { getJwtToken } from "@/lib/auth-client";

interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
    timestamp: Date;
}

interface AIChatProps {
    onTasksUpdated?: () => void;
}

export function AIChat({ onTasksUpdated }: AIChatProps) {
    const [messages, setMessages] = useState<Message[]>([
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
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Scroll to bottom when messages change
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const sendMessage = useCallback(async () => {
        if (!input.trim() || isLoading) return;

        const userMessage: Message = {
            id: `user-${Date.now()}`,
            role: "user",
            content: input.trim(),
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);
        setError(null);

        try {
            // Get JWT token
            const token = await getJwtToken();

            if (!token) {
                throw new Error("Not authenticated. Please log in again.");
            }

            // Send to AI Chat endpoint
            const response = await fetch("http://localhost:8000/api/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`,
                },
                body: JSON.stringify({
                    message: userMessage.content,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || errorData.error || `Request failed: ${response.status}`);
            }

            // Handle JSON response
            const data = await response.json();

            if (!data.success) {
                throw new Error(data.response || "AI request failed");
            }

            // Add assistant message
            setMessages(prev => [...prev, {
                id: `assistant-${Date.now()}`,
                role: "assistant",
                content: data.response,
                timestamp: new Date(),
            }]);

            // Notify parent that tasks may have been updated
            onTasksUpdated?.();

        } catch (err) {
            console.error("AI Chat error:", err);
            const errorMessage = err instanceof Error ? err.message : "An error occurred";

            setError(errorMessage);
            setMessages(prev => [...prev, {
                id: `error-${Date.now()}`,
                role: "assistant",
                content: `❌ ${errorMessage}

Please make sure the backend server is running and you have configured your OpenAI API key.`,
                timestamp: new Date(),
            }]);
        } finally {
            setIsLoading(false);
        }
    }, [input, isLoading, onTasksUpdated]);

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
                            <div className="ai-chat-message-text"
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

/**
 * Format message content with basic markdown support
 */
function formatMessage(content: string): string {
    return content
        // Bold
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        // Line breaks
        .replace(/\n/g, '<br />')
        // Code
        .replace(/`(.+?)`/g, '<code>$1</code>')
        // Bullet points
        .replace(/^- /gm, '• ');
}

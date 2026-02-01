/**
 * Chat API Client
 *
 * Custom SSE handler for AI chat streaming.
 *
 * NOTE: Do NOT use @openai/chatkit-react - build custom SSE handler.
 */

import { getJwtToken } from './auth-client';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

// =============================================================================
// Types
// =============================================================================

export interface ChatRequest {
  message: string;
  session_id?: string | null;
}

export type ChatStreamEvent =
  | ChatContentEvent
  | ChatToolCallEvent
  | ChatErrorEvent
  | ChatDoneEvent;

export interface ChatContentEvent {
  type: 'content';
  content: string;
  session_id?: string;
}

export interface ChatToolCallEvent {
  type: 'tool_call';
  tool_call: {
    id: string;
    name: string;
    arguments: Record<string, unknown>;
  };
}

export interface ChatErrorEvent {
  type: 'error';
  error: string;
}

export interface ChatDoneEvent {
  type: 'done';
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  tool_calls?: ToolCallInfo[];
}

export interface ToolCallInfo {
  id: string;
  name: string;
  arguments: Record<string, unknown>;
  result?: unknown;
}

// =============================================================================
// Chat API Client
// =============================================================================

export async function sendChatMessage(
  message: string,
  sessionId: string | null,
  onEvent: (event: ChatStreamEvent) => void,
  signal?: AbortSignal
): Promise<string> {
  const token = await getJwtToken();

  const response = await fetch(`${BACKEND_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ message, session_id: sessionId }),
    signal,
  });

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Session expired. Please log in again.');
    }
    throw new Error(`Chat error: ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();
  let newSessionId = sessionId || '';

  if (!reader) throw new Error('No response body');

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6)) as ChatStreamEvent;
            onEvent(data);

            if ('session_id' in data && data.session_id) {
              newSessionId = data.session_id;
            }
          } catch {
            // Ignore malformed JSON
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }

  return newSessionId;
}

// =============================================================================
// Utility Functions
// =============================================================================

export function formatMessage(content: string): string {
  /**
   * Format message content with basic markdown support
   */
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

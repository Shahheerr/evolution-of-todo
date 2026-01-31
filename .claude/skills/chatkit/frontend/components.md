# ChatKit Components

Built-in UI components for common chat patterns.

## Chat Component

The main pre-built chat UI.

```tsx
import { Chat } from '@openai/chatkit-react';

// Basic
<Chat />

// Full props
<Chat
    // Text customization
    placeholder="Ask me anything..."
    submitLabel="Send"
    loadingLabel="Thinking..."
    errorLabel="Something went wrong"
    
    // Behavior
    autoFocus={true}
    showTimestamps={true}
    showAvatars={true}
    
    // Styling
    className="custom-chat"
    theme="dark" // "light" | "dark" | "auto"
    
    // Callbacks
    onMessageSend={(content) => console.log("Sent:", content)}
    onResponse={(message) => console.log("Response:", message)}
    onError={(error) => console.error(error)}
/>
```

## MessageList

Display messages.

```tsx
import { MessageList } from '@openai/chatkit-react';

<MessageList
    messages={messages}
    showTimestamps={true}
    showAvatars={true}
    
    // Custom renderers
    renderMessage={(message) => (
        <div className={`msg ${message.role}`}>
            {message.content}
        </div>
    )}
    
    renderAvatar={(role) => (
        <span>{role === "user" ? "👤" : "🤖"}</span>
    )}
/>
```

## MessageInput

Text input with submit button.

```tsx
import { MessageInput } from '@openai/chatkit-react';

<MessageInput
    placeholder="Type here..."
    submitLabel="Send"
    
    // State
    value={input}
    onChange={setInput}
    onSubmit={handleSubmit}
    disabled={isLoading}
    
    // Features
    autoFocus={true}
    showSubmitButton={true}
    multiline={false}
    maxLength={2000}
/>
```

## Message Component

Single message display.

```tsx
import { Message } from '@openai/chatkit-react';

<Message
    role="assistant"
    content="Hello! How can I help?"
    timestamp={new Date()}
    
    // Appearance
    showAvatar={true}
    showTimestamp={true}
    
    // Custom avatar
    avatar={<span>🤖</span>}
/>
```

## LoadingIndicator

Shows while waiting for response.

```tsx
import { LoadingIndicator } from '@openai/chatkit-react';

<LoadingIndicator
    type="dots"  // "dots" | "spinner" | "pulse"
    label="Thinking..."
/>
```

## StreamingMessage

For displaying streaming content.

```tsx
import { StreamingMessage } from '@openai/chatkit-react';

<StreamingMessage
    content={streamingContent}
    showCursor={true}
    cursorChar="▊"
/>
```

## ErrorDisplay

Error message component.

```tsx
import { ErrorDisplay } from '@openai/chatkit-react';

<ErrorDisplay
    error={error}
    onRetry={handleRetry}
    retryLabel="Try again"
/>
```

## Composing Components

Build custom layouts:

```tsx
import {
    ChatKitProvider,
    MessageList,
    MessageInput,
    LoadingIndicator,
    ErrorDisplay,
    useChatMessages,
    useChatInput
} from '@openai/chatkit-react';

function CustomChatLayout() {
    const { messages, isLoading, error } = useChatMessages();
    const { input, setInput, submit } = useChatInput();
    
    return (
        <div className="custom-layout">
            {/* Header */}
            <header className="chat-header">
                <h1>Support Chat</h1>
            </header>
            
            {/* Messages area */}
            <main className="chat-main">
                <MessageList
                    messages={messages}
                    showTimestamps={true}
                />
                
                {isLoading && <LoadingIndicator type="dots" />}
                
                {error && (
                    <ErrorDisplay
                        error={error}
                        onRetry={() => location.reload()}
                    />
                )}
            </main>
            
            {/* Input area */}
            <footer className="chat-footer">
                <MessageInput
                    value={input}
                    onChange={setInput}
                    onSubmit={submit}
                    disabled={isLoading}
                    placeholder="Describe your issue..."
                />
            </footer>
        </div>
    );
}

export function SupportChat() {
    return (
        <ChatKitProvider url="/api/chatkit">
            <CustomChatLayout />
        </ChatKitProvider>
    );
}
```

## Component Styling

### CSS Variables

```css
:root {
    /* Colors */
    --chatkit-bg: #ffffff;
    --chatkit-text: #1f2937;
    --chatkit-border: #e5e7eb;
    --chatkit-primary: #3b82f6;
    
    /* User messages */
    --chatkit-user-bg: #3b82f6;
    --chatkit-user-text: #ffffff;
    
    /* Assistant messages */
    --chatkit-assistant-bg: #f3f4f6;
    --chatkit-assistant-text: #1f2937;
    
    /* Sizing */
    --chatkit-radius: 12px;
    --chatkit-padding: 16px;
    --chatkit-gap: 12px;
    
    /* Typography */
    --chatkit-font-family: system-ui, sans-serif;
    --chatkit-font-size: 14px;
}
```

### Class Names

```tsx
<Chat
    classNames={{
        container: "ck-container",
        header: "ck-header",
        messages: "ck-messages",
        message: "ck-message",
        userMessage: "ck-user",
        assistantMessage: "ck-assistant",
        input: "ck-input",
        inputField: "ck-input-field",
        submitButton: "ck-submit",
        loading: "ck-loading",
        error: "ck-error"
    }}
/>
```

## Dark Theme

```tsx
// Using theme prop
<Chat theme="dark" />

// Or with CSS
<style>
.dark-theme {
    --chatkit-bg: #1f2937;
    --chatkit-text: #f9fafb;
    --chatkit-border: #374151;
    --chatkit-assistant-bg: #374151;
}
</style>

<div className="dark-theme">
    <Chat />
</div>
```

## Responsive Design

```css
/* Mobile-first responsive chat */
.chat-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    max-height: 100vh;
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
}

.chat-input {
    padding: 1rem;
    border-top: 1px solid var(--chatkit-border);
}

@media (min-width: 768px) {
    .chat-container {
        max-width: 600px;
        margin: 0 auto;
        border-radius: 12px;
        max-height: 80vh;
    }
}
```

# Frontend API Client & UI Guidelines

## 1. Type-Safe API Client (`lib/api.ts`)
**Prompt Directive**: "Create a centralized API client that automatically handles Authorization headers and type-casts responses."

### **Core Responsibilities**
1.  **Token Injection**: Before *every* `fetch` call, invoke `getJwtToken()` from the Auth Client.
2.  **Authorization Header**: Append `Authorization: Bearer <token>`.
3.  **Error Handling**: If `401 Unauthorized` is received, assume the token expired and potentially redirect to login or clear cache.
4.  **Base URL**: Use `process.env.NEXT_PUBLIC_API_URL`.

### **Interface Strategy**
Define TypeScript interfaces that **exactly match** the Backend Pydantic models.
```typescript
interface TaskResponse {
  id: string;
  title: string;
  // ... other fields matching Pydantic
}
```

## 2. Component Architecture
- **Pages (`page.tsx`)**: Responsible for data fetching logic (using the API client) and state management.
- **Components (`TaskCard`, `TaskForm`)**: Pure UI components. Receive data via props.
- **Modals**: Use simple CSS/State-based modals for the "Create Task" flow.

## 3. Styling Guidelines (Tailwind)
**Prompt Directive**: "Use standard Tailwind utility classes. Do not use arbitrary values (e.g., `w-[325px]`) unless absolutely necessary."

- **Theme**: Dark Mode default (`bg-slate-900`, `text-slate-100`).
- **Interactive Elements**: Use `hover:` states for all buttons and cards.
- **Feedback**: Use loading spinners and toast/alert banners for async operations (`isPending` states).

## 4. State Management
- Use `useState` for local component state (Tasks list, Form inputs).
- Use `useEffect` to trigger data fetching on mount (if authenticated).
- **Optimization**: Use `useCallback` for event handlers passed to children.

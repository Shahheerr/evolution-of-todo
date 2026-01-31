# Better-Auth Configuration & JWT Strategy

## 1. Context
We do **NOT** use the standard Better-Auth JWT plugin for the backend communication because it requires specific `jwks` tables. Instead, we implement a **Custom Manual Token Exchange** pattern.

## 2. Server Configuration (`lib/auth.ts`)
**Prompt Directive**: "Configure Better-Auth as a pure session manager. Do NOT enable plugins that alter the database schema schema unpredictably."

### **Implementation Details**
- **File**: `frontend/lib/auth.ts`
- **Adapter**: `prismaAdapter`
- **Session Strategy**: Database-backed sessions (secure httpOnly cookies for the frontend).
- **Plugins**: NONE (Specifically removed `jwt` plugin).

```typescript
// STRICT CONFIGURATION PATTERN
export const auth = betterAuth({
  database: prismaAdapter(prisma, { provider: "postgresql" }),
  emailAndPassword: { enabled: true },
  session: { expiresIn: 60 * 60 * 24 * 7 }, // 7 Days
  secret: process.env.BETTER_AUTH_SECRET // MUST match Backend
  // NO PLUGINS HERE
});
```

## 3. JWT Generation Strategy (`/api/auth/token`)
**Prompt Directive**: "Create an explicit API route to mint Access Tokens for the Python Backend."

### **Token Specifications**
- **Library**: `jose` (`import * as jose from "jose"`)
- **Algorithm**: `HS256` (Symmetric)
- **Expiration**: 24 Hours (`24h`)
- **Required Claims**:
  - `sub`: User ID (Critical)
  - `email`: User Email
  - `name`: User Name
- **Forbidden Claims**: `aud` (Audience), `iss` (Issuer) - *These caused validation errors in Phase I and must be omitted.*

### **Code Reference**
```typescript
const secret = new TextEncoder().encode(process.env.BETTER_AUTH_SECRET);
const token = await new jose.SignJWT({
  sub: session.user.id, // CRITICAL: Backend uses this for RLS
  email: session.user.email
})
  .setProtectedHeader({ alg: "HS256" })
  .setIssuedAt()
  .setExpirationTime("24h")
  .sign(secret);
```

## 4. Client Integration
- **Hook**: `useSession()` works normally.
- **Token Retrieval**: The client must call `GET /api/auth/token` to get the raw string for the `Authorization` header.
- **Caching**: Implement simple in-memory caching for the token to avoid hitting the API route on every single request.

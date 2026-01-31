# Authentication Flow: The Stateless JWT Bridge

## 1. The Core Problem
We have a decoupled Frontend (Next.js) and Backend (FastAPI).
- **Frontend** handles the user login flow (UI, Redirects, Cookies).
- **Backend** needs to know "Who is this?" without maintaining session state or calling the Frontend for every request.

## 2. The Solution: Shared Secret JWT
Both systems share a `BETTER_AUTH_SECRET`. This acts as the cryptographic root of trust.

### **The Step-by-Step Flow**

#### **Phase A: Authentication (Frontend)**
1.  User enters credentials on `/auth/login`.
2.  **Better-Auth** verifies credentials against the `user` table in Neon.
3.  On success, Better-Auth establishes a session (cookie-based) for purely Frontend state.
4.  **Token Generation:** The Frontend calls an internal API route (e.g., `/api/auth/token`) that uses the server-side `BETTER_AUTH_SECRET` to sign a JWT containing:
    - `sub`: User ID
    - `exp`: Expiration time
    - `iat`: Issued at

#### **Phase B: Request (Frontend -> Backend)**
1.  Client wants to fetch tasks (`GET /tasks`).
2.  Frontend retrieves the JWT (from the internal API or hook state).
3.  Request is sent to FastAPI:
    ```http
    GET http://localhost:8000/tasks
    Authorization: Bearer eyJhbGciOiJIUzI1Ni...
    ```

#### **Phase C: Verification (Backend)**
1.  FastAPI receives the request.
2.  **Dependency Injection:** A security dependency (`get_current_user`) intercepts the request.
3.  **Verification:** Backend uses its copy of `BETTER_AUTH_SECRET` to attempt decoding the signature.
    - *Signature Invalid?* -> **401 Unauthorized** (Do not trust content).
    - *Expired?* -> **401 Unauthorized**.
4.  **Extraction:** Backend extracts `user_id` from the `sub` claim.
5.  **Execution:** The API endpoint executes, using `user_id` to strictly filter database results:
    `SELECT * FROM Task WHERE user_id = :decoded_user_id`

## 3. Security Rules (DO NOT BREAK)
1.  **NEVER** expose `BETTER_AUTH_SECRET` to the client-side bundle (Next.js `NEXT_PUBLIC_` prefix is FORBIDDEN for this secret).
2.  **ALWAYS** verify the algorithm matches (HS256).
3.  Backend relies **solely** on the token. It does not check the `session` table in the DB for performance reasons (Stateless).

## 4. Resources
- [Better-Auth Documentation](https://www.better-auth.com/docs)
- [JWT.io Debugger](https://jwt.io/)
- [FastAPI OAuth2 with JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)

/**
 * Better Auth Client Configuration
 * 
 * This is the client-side auth instance used in React components.
 * It provides hooks and methods for:
 * - Sign in / Sign up
 * - Sign out
 * - Get current session
 * - Get JWT token for API calls
 */

import { createAuthClient } from "better-auth/react";

// Create the auth client
export const authClient = createAuthClient({
    baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
});

// Export commonly used hooks and methods
export const {
    signIn,
    signUp,
    signOut,
    useSession,
    getSession,
} = authClient;

// Token cache
let cachedToken: string | null = null;
let tokenExpiry: number = 0;

/**
 * Get the JWT token for API authentication.
 * Use this token in the Authorization header when calling FastAPI.
 * 
 * @returns Promise<string | null> - The JWT token or null if not authenticated
 */
export async function getJwtToken(): Promise<string | null> {
    // Check if we have a valid cached token
    const now = Date.now();
    if (cachedToken && tokenExpiry > now) {
        return cachedToken;
    }

    try {
        // Fetch the JWT from our custom token endpoint
        const response = await fetch("/api/auth/token", {
            method: "GET",
            credentials: "include",
        });

        if (response.ok) {
            const data = await response.json();
            if (data.token) {
                cachedToken = data.token;
                // Cache for 23 hours (token expires in 24 hours)
                tokenExpiry = now + (23 * 60 * 60 * 1000);
                return cachedToken;
            }
        }

        // Clear cache on failure
        cachedToken = null;
        tokenExpiry = 0;
        return null;
    } catch (error) {
        console.error("Failed to get JWT token:", error);
        cachedToken = null;
        tokenExpiry = 0;
        return null;
    }
}

/**
 * Clear the token cache (call on sign out)
 */
export function clearTokenCache(): void {
    cachedToken = null;
    tokenExpiry = 0;
}

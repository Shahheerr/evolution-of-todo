/**
 * Better Auth Server Configuration
 * 
 * This is the core authentication setup that handles:
 * - User registration and login
 * - Session management
 * - JWT token generation for API authentication
 */

import { betterAuth } from "better-auth";
import { prismaAdapter } from "better-auth/adapters/prisma";
import { PrismaClient } from "@/app/generated/prisma";

// Initialize Prisma Client
const prisma = new PrismaClient();

export const auth = betterAuth({
    // Database adapter - uses Prisma with PostgreSQL
    database: prismaAdapter(prisma, {
        provider: "postgresql",
    }),

    // Email & Password authentication
    emailAndPassword: {
        enabled: true,
        requireEmailVerification: false, // Set to true in production
    },

    // Session configuration
    session: {
        expiresIn: 60 * 60 * 24 * 7, // 7 days
        updateAge: 60 * 60 * 24, // Update session every 24 hours
        cookieCache: {
            enabled: true,
            maxAge: 60 * 5, // Cache for 5 minutes
        },
    },

    // Secret for signing tokens (from environment)
    secret: process.env.BETTER_AUTH_SECRET,

    // Base URL for callbacks
    baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",

    // Trust host header
    trustedOrigins: [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
});

// Export auth types for TypeScript
export type Session = typeof auth.$Infer.Session;
export type User = typeof auth.$Infer.Session.user;

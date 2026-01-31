/**
 * JWT Token API Route
 * 
 * This endpoint returns the JWT token for the authenticated user.
 * The frontend calls this to get a token for FastAPI requests.
 */

import { auth } from "@/lib/auth";
import { headers } from "next/headers";
import { NextResponse } from "next/server";
import * as jose from "jose";

export async function GET() {
    try {
        // Get the session from Better Auth
        const session = await auth.api.getSession({
            headers: await headers(),
        });

        if (!session) {
            return NextResponse.json(
                { error: "Not authenticated" },
                { status: 401 }
            );
        }

        // Generate a JWT token manually using the same secret as Better Auth
        const secret = new TextEncoder().encode(process.env.BETTER_AUTH_SECRET);

        const token = await new jose.SignJWT({
            sub: session.user.id,
            email: session.user.email,
            name: session.user.name,
        })
            .setProtectedHeader({ alg: "HS256" })
            .setIssuedAt()
            .setExpirationTime("24h")
            .sign(secret);

        return NextResponse.json({ token });
    } catch (error) {
        console.error("Failed to generate JWT:", error);
        return NextResponse.json(
            { error: "Failed to generate token" },
            { status: 500 }
        );
    }
}

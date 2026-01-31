"use client";

import Link from "next/link";
import { useSession } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function HomePage() {
  const { data: session, isPending } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (session && !isPending) {
      router.push("/dashboard");
    }
  }, [session, isPending, router]);

  if (isPending) {
    return (
      <div className="loading-overlay" style={{ minHeight: "100vh" }}>
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh" }}>
      {/* Navigation */}
      <nav style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "1.5rem 2rem",
        maxWidth: "1200px",
        margin: "0 auto",
      }}>
        <div style={{
          fontSize: "1.5rem",
          fontWeight: "700",
          background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
        }}>
          ✨ TaskFlow
        </div>
        <div className="flex gap-md">
          <Link href="/auth/login" className="btn btn-ghost">
            Sign In
          </Link>
          <Link href="/auth/register" className="btn btn-primary">
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
        padding: "4rem 2rem",
        maxWidth: "800px",
        margin: "0 auto",
      }}>
        <div style={{
          display: "inline-block",
          padding: "0.5rem 1rem",
          background: "rgba(99, 102, 241, 0.1)",
          border: "1px solid rgba(99, 102, 241, 0.3)",
          borderRadius: "9999px",
          fontSize: "0.875rem",
          color: "#818cf8",
          marginBottom: "1.5rem",
        }}>
          🚀 Production-Ready Todo App
        </div>

        <h1 style={{
          fontSize: "3.5rem",
          fontWeight: "800",
          lineHeight: "1.1",
          marginBottom: "1.5rem",
          background: "linear-gradient(135deg, #f8fafc 0%, #94a3b8 100%)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
        }}>
          Organize Your Life with <span style={{
            background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}>TaskFlow</span>
        </h1>

        <p style={{
          fontSize: "1.25rem",
          color: "#94a3b8",
          maxWidth: "600px",
          marginBottom: "2rem",
          lineHeight: "1.7",
        }}>
          A beautifully designed task management app with priorities, tags,
          smart filtering, and secure JWT authentication.
        </p>

        <div className="flex gap-md" style={{ marginBottom: "4rem" }}>
          <Link href="/auth/register" className="btn btn-primary btn-lg">
            Start Free →
          </Link>
          <Link href="/auth/login" className="btn btn-secondary btn-lg">
            Sign In
          </Link>
        </div>

        {/* Features Grid */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "1.5rem",
          width: "100%",
          marginTop: "2rem",
        }}>
          {[
            { icon: "📝", title: "Full CRUD", desc: "Create, edit, delete tasks" },
            { icon: "🏷️", title: "Tags & Priority", desc: "Organize with labels" },
            { icon: "🔍", title: "Smart Search", desc: "Find tasks instantly" },
            { icon: "🔐", title: "Secure Auth", desc: "JWT-based security" },
          ].map((feature, i) => (
            <div key={i} className="card" style={{ textAlign: "center" }}>
              <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>
                {feature.icon}
              </div>
              <h3 style={{ fontSize: "1rem", marginBottom: "0.25rem" }}>
                {feature.title}
              </h3>
              <p style={{ fontSize: "0.875rem", color: "#64748b" }}>
                {feature.desc}
              </p>
            </div>
          ))}
        </div>
      </main>

      {/* Footer */}
      <footer style={{
        textAlign: "center",
        padding: "2rem",
        color: "#64748b",
        fontSize: "0.875rem",
      }}>
        Built with Next.js, FastAPI, and Better Auth
      </footer>
    </div>
  );
}

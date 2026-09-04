"use client";

import React from "react";
import Link from "next/link";

// Icons
const ArrowRight = ({ className = "", size = 16 }: { className?: string; size?: number }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <path d="M5 12h14" />
    <path d="m12 5 7 7-7 7" />
  </svg>
);

const Menu = ({ size = 24 }: { size?: number }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="4" x2="20" y1="12" y2="12" />
    <line x1="4" x2="20" y1="6" y2="6" />
    <line x1="4" x2="20" y1="18" y2="18" />
  </svg>
);

const X = ({ size = 24 }: { size?: number }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M18 6 6 18" />
    <path d="m6 6 12 12" />
  </svg>
);

// Navigation
const Navigation = React.memo(() => {
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  return (
    <header
      className="fixed top-0 w-full z-50 backdrop-blur-md"
      style={{
        background: "rgba(24, 24, 28, 0.85)",
        borderBottom: "1px solid rgba(255,255,255,0.05)",
        boxShadow: "0 4px 24px rgba(0,0,0,0.6), 0 -1px 0 rgba(255,255,255,0.04) inset",
      }}
    >
      <nav className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <Link
            href="/"
            className="flex items-center transition-opacity hover:opacity-90"
            style={{ color: "#eee" }}
          >
            <span style={{ fontFamily: "'Kola', sans-serif", fontSize: "1.75rem", letterSpacing: "0.04em", textTransform: "uppercase" }}>ARBITER</span>
          </Link>

          <div className="hidden md:flex items-center gap-4">
            <Link href="/dashboard">
              <button
                className="neo-button-accent rounded-xl px-5 py-2 text-sm font-semibold"
                style={{ color: "#0e0e12" }}
              >
                Dashboard →
              </button>
            </Link>
          </div>

          <button
            className="md:hidden text-white"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </nav>

      {mobileMenuOpen && (
        <div
          className="md:hidden backdrop-blur-md px-6 py-4"
          style={{
            background: "rgba(18, 18, 22, 0.97)",
            borderTop: "1px solid rgba(255,255,255,0.05)",
            animation: "slideDown 0.25s ease-out",
          }}
        >
          <Link href="/dashboard" onClick={() => setMobileMenuOpen(false)}>
            <button
              className="neo-button-accent rounded-xl px-5 py-2 text-sm font-semibold w-full"
              style={{ color: "#0e0e12" }}
            >
              Dashboard →
            </button>
          </Link>
        </div>
      )}
    </header>
  );
});
Navigation.displayName = "Navigation";

// Hero
const Hero = React.memo(() => {
  return (
    <section
      className="relative min-h-screen flex flex-col items-center justify-start px-6 py-20 md:py-28"
      style={{ background: "#0a0a0f", animation: "fadeIn 0.6s ease-out" }}
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
        h1, h2, h3, p, span, a, button, aside { font-family: 'Poppins', sans-serif; }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(12px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes slideDown {
          from { opacity: 0; transform: translateY(-10px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}</style>

      {/* Badge Pill — neomorphic inset pill */}
      <aside
        className="mb-8 inline-flex flex-wrap items-center justify-center gap-2 px-5 py-2.5 rounded-full"
        style={{
          background: "rgb(28 28 34)",
          boxShadow: "inset 3px 3px 7px rgba(0,0,0,0.7), inset -3px -3px 7px rgba(255,255,255,0.05)",
          border: "none",
        }}
      >
        <span className="text-xs text-center whitespace-nowrap font-medium" style={{ color: "rgb(217 158 73)" }}>
          ⚡ Rules Engine + AI Agent, Working Side-by-Side
        </span>
      </aside>

      {/* Headline */}
      <h1
        className="text-4xl md:text-5xl lg:text-6xl font-semibold text-center max-w-3xl px-6 leading-tight mb-6"
        style={{
          background: "linear-gradient(to bottom, #ffffff 0%, #ffffff 55%, rgba(255,255,255,0.55) 100%)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
          backgroundClip: "text",
          letterSpacing: "-0.05em",
        }}
      >
        Every failed payment <br />deserves a second opinion
      </h1>

      {/* Subheading */}
      <p
        className="text-sm md:text-base text-center max-w-2xl px-6 mb-10 leading-relaxed"
        style={{ color: "rgb(110 107 98)" }}
      >
        Arbiter classifies failed payments with a rules engine AND an AI reasoning agent
        side-by-side, weighs both, and executes real recovery actions in Razorpay test mode —
        retries, delayed retries, and alternate payment links.
      </p>

      {/* CTA */}
      <div className="flex items-center gap-4 relative z-10 mb-16">
        <Link href="/dashboard">
          <button
            className="neo-button-accent inline-flex items-center gap-2 rounded-xl px-8 py-3.5 text-base font-semibold"
            style={{ color: "#0e0e12" }}
          >
            Try the Dashboard <ArrowRight size={16} />
          </button>
        </Link>
      </div>

      {/* Hero image frame */}
      <div className="w-full max-w-5xl relative pb-20">
        {/* Glow background blob */}
        <div
          className="absolute left-1/2 w-[75%] pointer-events-none z-0"
          style={{
            top: "-8%",
            transform: "translateX(-50%)",
            height: "260px",
            background: "radial-gradient(ellipse, rgba(217,158,73,0.12) 0%, transparent 70%)",
            filter: "blur(40px)",
          }}
          aria-hidden="true"
        />

        {/* Neomorphic image frame */}
        <div
          className="relative z-10 p-2.5 rounded-2xl"
          style={{
            background: "rgb(28 28 34)",
            boxShadow: "8px 8px 20px rgba(0,0,0,0.85), -6px -6px 16px rgba(255,255,255,0.05), 0 0 40px rgba(217,158,73,0.08)",
          }}
        >
          <img
            src="/dashboard-preview.png"
            alt="Arbiter Dashboard Preview — payment events with Rules vs AI reasoning"
            className="w-full h-auto rounded-xl"
            style={{
              boxShadow: "inset 0 0 0 1px rgba(255,255,255,0.06)",
            }}
            loading="eager"
          />
        </div>
      </div>
    </section>
  );
});
Hero.displayName = "Hero";

// Main
export default function LandingPage() {
  return (
    <main style={{ minHeight: "100vh", background: "#0a0a0f", color: "#eeedea" }}>
      <Navigation />
      <Hero />
    </main>
  );
}

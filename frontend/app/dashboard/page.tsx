"use client";

import { useEffect, useState, useCallback } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ── Types ────────────────────────────────────────────────────────────────────
interface SummaryData {
  revenue_recovered_with_agent: number;
  revenue_recovered_without_agent: number;
  revenue_recovered_with_agent_formatted: string;
  revenue_recovered_without_agent_formatted: string;
  total_events: number;
  events_by_category: Record<string, number>;
  ai_agreement_count?: number;
  total_ai_classified?: number;
}
interface RulesEnginePayload {
  category: string; action: string; action_type: string; rationale: string;
}
interface AIAgentPayload {
  category: string; action: string; action_type: string; rationale: string;
  reasoning_notes: string; confidence: number;
}
interface EventItem {
  id: string; razorpay_payment_id: string; time: string; amount: string;
  amount_paise: number; failure_reason: string; failure_reason_code: string;
  action_taken: string; action_type: string;
  status: "recovered" | "pending" | "failed" | "no action taken";
  customer_email?: string; customer_phone?: string;
  event_source?: "synthetic" | "razorpay_webhook" | "razorpay_test_ping" | string;
  executed?: boolean; executed_at?: string;
  razorpay_payment_link_id?: string; razorpay_payment_link_url?: string;
  razorpay_short_url?: string; execution_error?: string;
  category?: string; rules_engine?: RulesEnginePayload;
  ai_agent?: AIAgentPayload; agreement?: boolean;
}

// ── Design tokens ────────────────────────────────────────────────────────────
const T = {
  white:     "#f5f5f5",
  gray:      "#a3a3a3",
  grayDim:   "#737373",
  orange:    "rgb(251,146,60)",
  green:     "rgb(74,198,130)",
  red:       "rgb(239,68,68)",
  poppins:   "var(--font-nippo), 'Nippo', sans-serif",
  mono:      "var(--font-nippo), 'Nippo', sans-serif",
} as const;

// ── Fixed background layer ────────────────────────────────────────────────────
function BackgroundLayer() {
  return (
    <div
      aria-hidden="true"
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 0,
        pointerEvents: "none",
        overflow: "hidden",
        background: "#000000",
      }}
    >
      {/* Blob 1 — top-left, primary orange glow */}
      <div style={{
        position: "absolute",
        top: "-200px",
        left: "-150px",
        width: "700px",
        height: "700px",
        borderRadius: "50%",
        background: "radial-gradient(circle at 40% 40%, rgba(251,146,60,0.13) 0%, rgba(251,146,60,0.04) 45%, transparent 70%)",
        filter: "blur(80px)",
      }} />
      {/* Blob 2 — bottom-right */}
      <div style={{
        position: "absolute",
        bottom: "-220px",
        right: "-160px",
        width: "760px",
        height: "760px",
        borderRadius: "50%",
        background: "radial-gradient(circle at 55% 55%, rgba(251,146,60,0.10) 0%, rgba(234,88,12,0.04) 45%, transparent 70%)",
        filter: "blur(100px)",
      }} />
      {/* Blob 3 — center, behind main table area */}
      <div style={{
        position: "absolute",
        top: "38%",
        left: "50%",
        transform: "translateX(-50%)",
        width: "520px",
        height: "280px",
        borderRadius: "50%",
        background: "radial-gradient(ellipse, rgba(251,146,60,0.07) 0%, transparent 70%)",
        filter: "blur(90px)",
      }} />
    </div>
  );
}

// ── Stat Card ────────────────────────────────────────────────────────────────
function StatCard({
  label, value, subtitle, variant = "neutral", loading,
}: {
  label: string; value: string; subtitle?: string;
  variant?: "neutral" | "accent"; loading?: boolean;
}) {
  const isAccent = variant === "accent";

  return (
    <div
      className="glass-panel-strong"
      style={{
        padding: "1.75rem",
        display: "flex",
        flexDirection: "column" as const,
        gap: "0.875rem",
        ...(isAccent ? { borderColor: "rgba(251,146,60,0.2)" } : {}),
      }}
    >
      {/* Label */}
      <span style={{
        fontFamily: T.poppins,
        fontSize: "0.62rem",
        fontWeight: 600,
        letterSpacing: "0.1em",
        textTransform: "uppercase" as const,
        color: isAccent ? T.orange : T.grayDim,
      }}>
        {label}
      </span>

      {/* Figure */}
      <span
        className="tabular-nums"
        style={{
          fontFamily: T.poppins,
          fontSize: "2.4rem",
          fontWeight: 700,
          lineHeight: 1,
          letterSpacing: "-0.03em",
          color: isAccent ? T.orange : T.white,
        }}
      >
        {loading ? (
          <span style={{ display: "inline-block", width: "7rem", height: "2.4rem", borderRadius: "8px", background: "rgba(255,255,255,0.06)" }} />
        ) : value}
      </span>

      {/* Context line */}
      <span style={{
        fontFamily: T.poppins,
        fontSize: "0.72rem",
        fontWeight: 400,
        color: isAccent ? T.orange : T.gray,
        opacity: isAccent ? 0.8 : 0.75,
      }}>
        {subtitle || (loading ? "Updating…" : "Live baseline")}
      </span>
    </div>
  );
}

// ── Status Badge — solid fills, NOT glass ─────────────────────────────────────
function StatusBadge({ status }: { status: string }) {
  const base: React.CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    gap: "0.35rem",
    borderRadius: "999px",
    padding: "0.22rem 0.65rem",
    fontSize: "0.68rem",
    fontFamily: T.poppins,
    fontWeight: 600,
    whiteSpace: "nowrap" as const,
    lineHeight: 1.4,
  };
  switch (status) {
    case "recovered": case "executed":
      return <span style={{ ...base, background: "rgba(74,198,130,0.18)", color: T.green, border: "1px solid rgba(74,198,130,0.35)" }}>
        <span style={{ width: 5, height: 5, borderRadius: "50%", background: T.green, flexShrink: 0 }} />Recovered
      </span>;
    case "failed": case "execution_failed":
      return <span style={{ ...base, background: "rgba(239,68,68,0.16)", color: T.red, border: "1px solid rgba(239,68,68,0.32)" }}>
        <span style={{ width: 5, height: 5, borderRadius: "50%", background: T.red, flexShrink: 0 }} />Failed
      </span>;
    case "pending (delayed)":
      return <span style={{ ...base, background: "rgba(251,146,60,0.16)", color: T.orange, border: "1px solid rgba(251,146,60,0.32)" }}>
        <span style={{ width: 5, height: 5, borderRadius: "50%", background: T.orange, flexShrink: 0 }} />Pending (Delayed)
      </span>;
    case "pending":
      return <span style={{ ...base, background: "rgba(251,146,60,0.16)", color: T.orange, border: "1px solid rgba(251,146,60,0.32)" }}>
        <span style={{ width: 5, height: 5, borderRadius: "50%", background: T.orange, flexShrink: 0 }} />Pending
      </span>;
    default:
      return <span style={{ ...base, background: "rgba(255,255,255,0.06)", color: T.gray, border: "1px solid rgba(255,255,255,0.09)" }}>
        <span style={{ width: 5, height: 5, borderRadius: "50%", background: "rgba(163,163,163,0.4)", flexShrink: 0 }} />No Action
      </span>;
  }
}

// ── Source Badge ─────────────────────────────────────────────────────────────
function SourceBadge({ source }: { source?: string }) {
  const chip: React.CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    gap: "0.25rem",
    borderRadius: "6px",
    padding: "0.12rem 0.45rem",
    fontSize: "0.62rem",
    fontFamily: T.mono,
    fontWeight: 500,
    whiteSpace: "nowrap" as const,
  };
  if (source === "razorpay_webhook")
    return <span style={{ ...chip, background: "rgba(251,146,60,0.1)", color: T.orange, border: "1px solid rgba(251,146,60,0.22)" }}>⚡ Live Webhook</span>;
  if (source === "razorpay_test_ping")
    return <span style={{ ...chip, background: "rgba(255,255,255,0.04)", color: T.grayDim, border: "1px solid rgba(255,255,255,0.07)" }}>🧪 Test Ping</span>;
  return <span style={{ ...chip, background: "rgba(255,255,255,0.04)", color: T.grayDim, border: "1px solid rgba(255,255,255,0.06)" }}>Demo Data</span>;
}

// ── Events Table ─────────────────────────────────────────────────────────────
const COLS = ["Time / Source", "Amount", "Failure Reason", "Action Taken", "Status", "Details"] as const;

function EventsTable({ events, loading }: { events: EventItem[]; loading: boolean }) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const toggle = (id: string) => setExpandedId((p) => (p === id ? null : id));

  const realCount = events.filter((e) => e.event_source === "razorpay_webhook").length;
  const testCount = events.filter((e) => e.event_source === "razorpay_test_ping").length;
  const demoCount = events.filter((e) => e.event_source !== "razorpay_webhook" && e.event_source !== "razorpay_test_ping").length;

  return (
    <div className="glass-panel-strong" style={{ overflow: "hidden" }}>
      {/* Header */}
      <div style={{
        padding: "1rem 1.5rem",
        display: "flex",
        flexWrap: "wrap" as const,
        alignItems: "center",
        justifyContent: "space-between",
        gap: "0.75rem",
        borderBottom: "1px solid rgba(255,255,255,0.07)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <h2 style={{ fontFamily: T.poppins, fontSize: "0.88rem", fontWeight: 600, color: T.white, margin: 0 }}>
            Payment Events
          </h2>
          <span style={{ fontFamily: T.poppins, fontSize: "0.68rem", color: T.grayDim }}>
            Click any row for reasoning &amp; links
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          {[
            `${realCount} live`,
            `${demoCount} demo`,
            ...(testCount > 0 ? [`${testCount} test`] : []),
            loading ? "Loading…" : `${events.length} total`,
          ].map((label) => (
            <span key={label} style={{ fontFamily: T.mono, fontSize: "0.6rem", color: T.grayDim, background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.07)", borderRadius: "999px", padding: "0.18rem 0.6rem" }}>
              {label}
            </span>
          ))}
        </div>
      </div>

      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              {COLS.map((c) => (
                <th key={c} style={{ padding: "0.7rem 1.25rem", textAlign: "left", fontSize: "0.6rem", fontFamily: T.poppins, fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase" as const, color: T.grayDim, borderBottom: "1px solid rgba(255,255,255,0.06)", whiteSpace: "nowrap" as const }}>
                  {c}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {events.length === 0 ? (
              <tr>
                <td colSpan={COLS.length} style={{ padding: "4rem 1.5rem", textAlign: "center" }}>
                  <div style={{ display: "flex", flexDirection: "column" as const, alignItems: "center", gap: "0.75rem" }}>
                    <span style={{ fontSize: "1.75rem" }}>⚡</span>
                    <p style={{ fontFamily: T.poppins, fontWeight: 600, color: T.gray, margin: 0 }}>
                      {loading ? "Loading payment events…" : "No payment events yet"}
                    </p>
                    <p style={{ fontFamily: T.poppins, fontSize: "0.75rem", color: T.grayDim, maxWidth: "22rem", margin: 0, lineHeight: 1.6 }}>
                      Events will appear here once synthetic events are generated or Razorpay webhooks start flowing in.
                    </p>
                  </div>
                </td>
              </tr>
            ) : events.map((ev) => {
              const expanded = expandedId === ev.id;
              const time = new Date(ev.time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
              const date = new Date(ev.time).toLocaleDateString([], { month: "short", day: "numeric" });
              const linkUrl = ev.razorpay_short_url || ev.razorpay_payment_link_url;

              return (
                <tr key={ev.id}>
                  <td colSpan={COLS.length} style={{ padding: 0 }}>
                    {/* Row — no glass here, just transparent */}
                    <div
                      onClick={() => toggle(ev.id)}
                      style={{
                        display: "grid",
                        gridTemplateColumns: "200px 110px 1fr 160px 150px 100px",
                        gap: "0.75rem",
                        padding: "0.875rem 1.25rem",
                        alignItems: "center",
                        cursor: "pointer",
                        borderBottom: expanded ? "none" : "1px solid rgba(255,255,255,0.04)",
                        background: expanded ? "rgba(255,255,255,0.025)" : "transparent",
                        transition: "background 0.12s ease",
                      }}
                      onMouseEnter={(e) => { if (!expanded) (e.currentTarget as HTMLDivElement).style.background = "rgba(255,255,255,0.02)"; }}
                      onMouseLeave={(e) => { if (!expanded) (e.currentTarget as HTMLDivElement).style.background = "transparent"; }}
                    >
                      <div style={{ display: "flex", flexDirection: "column" as const, gap: "0.3rem" }}>
                        <span style={{ fontFamily: T.mono, fontSize: "0.68rem", color: T.gray }}>
                          {time} <span style={{ fontSize: "0.6rem", color: T.grayDim }}>({date})</span>
                        </span>
                        <SourceBadge source={ev.event_source} />
                      </div>

                      <span style={{ fontFamily: T.poppins, fontSize: "0.9rem", fontWeight: 700, color: T.white, whiteSpace: "nowrap" as const }}>
                        {ev.amount}
                      </span>

                      <div>
                        <div style={{ fontFamily: T.poppins, fontSize: "0.78rem", fontWeight: 500, color: T.white, lineHeight: 1.4 }}>{ev.failure_reason}</div>
                        {ev.customer_email && <div style={{ fontFamily: T.mono, fontSize: "0.62rem", color: T.grayDim, marginTop: "0.15rem" }}>{ev.customer_email}</div>}
                      </div>

                      <span style={{ fontFamily: T.poppins, fontSize: "0.75rem", color: T.gray, whiteSpace: "nowrap" as const }}>{ev.action_taken}</span>
                      <div style={{ whiteSpace: "nowrap" as const }}><StatusBadge status={ev.status} /></div>

                      <div style={{ display: "flex", justifyContent: "flex-end" }}>
                        <span style={{ fontFamily: T.poppins, fontSize: "0.62rem", fontWeight: 500, color: T.grayDim, background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.09)", borderRadius: "7px", padding: "0.22rem 0.55rem", whiteSpace: "nowrap" as const }}>
                          {expanded ? "Hide ▲" : "Details ▼"}
                        </span>
                      </div>
                    </div>

                    {/* Expanded detail — glass container, no nested blur on children */}
                    {expanded && (
                      <div style={{
                        padding: "1.25rem 1.5rem",
                        background: "rgba(0,0,0,0.6)",
                        borderTop: "1px solid rgba(255,255,255,0.05)",
                        borderBottom: "1px solid rgba(255,255,255,0.05)",
                        display: "flex",
                        flexDirection: "column" as const,
                        gap: "1rem",
                      }}>
                        {/* Razorpay link / status */}
                        {linkUrl ? (
                          <div style={{
                            padding: "0.875rem 1.125rem",
                            background: "rgba(251,146,60,0.08)",
                            border: "1px solid rgba(251,146,60,0.22)",
                            borderRadius: "12px",
                            display: "flex",
                            flexWrap: "wrap" as const,
                            alignItems: "center",
                            justifyContent: "space-between",
                            gap: "0.75rem",
                          }}>
                            <div style={{ display: "flex", flexDirection: "column" as const, gap: "0.2rem" }}>
                              <span style={{ fontFamily: T.poppins, fontSize: "0.7rem", fontWeight: 600, color: T.orange }}>
                                💳 Autonomously Generated Razorpay Payment Link
                              </span>
                              {ev.razorpay_payment_link_id && (
                                <span style={{ fontFamily: T.mono, fontSize: "0.62rem", color: T.grayDim }}>
                                  ID: {ev.razorpay_payment_link_id}
                                </span>
                              )}
                            </div>
                            <a
                              href={linkUrl}
                              target="_blank"
                              rel="noreferrer"
                              onClick={(e) => e.stopPropagation()}
                              style={{
                                display: "inline-flex",
                                alignItems: "center",
                                gap: "0.375rem",
                                padding: "0.45rem 0.875rem",
                                borderRadius: "9px",
                                fontSize: "0.72rem",
                                fontFamily: T.poppins,
                                fontWeight: 700,
                                background: T.orange,
                                color: "#000",
                                textDecoration: "none",
                                boxShadow: "0 3px 12px rgba(251,146,60,0.3)",
                              }}
                            >
                              🔗 View Payment Link ↗
                            </a>
                          </div>
                        ) : ev.execution_error ? (
                          <div style={{ padding: "0.75rem 1rem", background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.22)", borderRadius: "10px", fontSize: "0.72rem", fontFamily: T.poppins, color: T.red }}>
                            ⚠️ Execution failed: {ev.execution_error}
                          </div>
                        ) : ev.executed ? (
                          <div style={{ padding: "0.75rem 1rem", background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "10px", fontSize: "0.72rem", fontFamily: T.poppins, color: T.gray }}>
                            ✓ Action executed (No external link required for {ev.action_taken})
                          </div>
                        ) : (
                          <div style={{ padding: "0.75rem 1rem", background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.07)", borderRadius: "10px", fontSize: "0.72rem", fontFamily: T.poppins, color: T.grayDim }}>
                            Not yet executed
                          </div>
                        )}

                        {/* Reasoning header */}
                        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingBottom: "0.75rem", borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
                          <span style={{ fontFamily: T.poppins, fontSize: "0.6rem", fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase" as const, color: T.grayDim }}>
                            Side-by-Side Reasoning Comparison
                          </span>
                          {ev.agreement !== undefined && (
                            <span style={{
                              fontFamily: T.poppins, fontSize: "0.68rem", fontWeight: 600, borderRadius: "999px", padding: "0.18rem 0.65rem",
                              background: ev.agreement ? "rgba(74,198,130,0.12)" : "rgba(251,146,60,0.12)",
                              color: ev.agreement ? T.green : T.orange,
                              border: `1px solid ${ev.agreement ? "rgba(74,198,130,0.28)" : "rgba(251,146,60,0.28)"}`,
                            }}>
                              {ev.agreement ? "✓ Rules & AI Agreed" : "⚡ AI Nuance Disagreement"}
                            </span>
                          )}
                        </div>

                        {/* Comparison cards — .glass-panel, NO nested blur */}
                        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "0.875rem" }}>
                          {/* Rules Engine card */}
                          <div className="glass-panel" style={{ padding: "1.125rem", display: "flex", flexDirection: "column" as const, gap: "0.6rem" }}>
                            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                              <span style={{ fontFamily: T.poppins, fontSize: "0.72rem", fontWeight: 600, color: T.gray }}>
                                ⚙️ Rules Engine
                              </span>
                              <span style={{ fontFamily: T.mono, fontSize: "0.58rem", color: T.grayDim, background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "5px", padding: "0.12rem 0.45rem" }}>
                                Static Policy
                              </span>
                            </div>
                            <div style={{ fontFamily: T.poppins, fontSize: "0.75rem", fontWeight: 600, color: T.white }}>
                              Action: {ev.rules_engine?.action || ev.action_taken}
                            </div>
                            <p style={{ fontFamily: T.poppins, fontSize: "0.72rem", color: T.gray, lineHeight: 1.65, margin: 0 }}>
                              {ev.rules_engine?.rationale || "Generic category fallback applied."}
                            </p>
                          </div>

                          {/* AI Agent card — orange-tinted border glow */}
                          <div className="glass-panel-ai" style={{ padding: "1.125rem", display: "flex", flexDirection: "column" as const, gap: "0.6rem" }}>
                            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                              <span style={{ fontFamily: T.poppins, fontSize: "0.72rem", fontWeight: 600, color: T.orange }}>
                                🤖 AI Reasoning Agent
                              </span>
                              {ev.ai_agent?.confidence !== undefined && (
                                <span style={{ fontFamily: T.mono, fontSize: "0.58rem", color: T.grayDim, background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "5px", padding: "0.12rem 0.45rem" }}>
                                  Conf: {Math.round(ev.ai_agent.confidence * 100)}%
                                </span>
                              )}
                            </div>
                            <div style={{ fontFamily: T.poppins, fontSize: "0.75rem", fontWeight: 600, color: T.orange }}>
                              Recommended: {ev.ai_agent?.action || ev.action_taken}
                            </div>
                            <p style={{ fontFamily: T.poppins, fontSize: "0.72rem", color: T.white, lineHeight: 1.65, margin: 0 }}>
                              {ev.ai_agent?.rationale || "AI contextual reasoning generated."}
                            </p>

                            {ev.ai_agent?.reasoning_notes && (
                              /* AI Nuance callout — solid tinted, no nested blur */
                              <div style={{
                                marginTop: "0.25rem",
                                padding: "0.625rem 0.75rem",
                                background: "rgba(251,146,60,0.08)",
                                border: "1px solid rgba(251,146,60,0.2)",
                                borderRadius: "10px",
                              }}>
                                <div style={{ fontFamily: T.poppins, fontSize: "0.62rem", fontWeight: 700, color: T.orange, marginBottom: "0.3rem" }}>
                                  💡 AI Nuance &amp; Overlook Factor:
                                </div>
                                <p style={{ fontFamily: T.poppins, fontSize: "0.68rem", color: T.gray, fontStyle: "italic", lineHeight: 1.65, margin: 0 }}>
                                  "{ev.ai_agent.reasoning_notes}"
                                </p>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ── Header ────────────────────────────────────────────────────────────────────
function Header({
  onRefresh, onProcessAI, onExecutePending, onProcessDue,
  loading, aiProcessing, executing,
}: {
  onRefresh: () => void; onProcessAI: () => void;
  onExecutePending: () => void; onProcessDue: () => void;
  loading: boolean; aiProcessing: boolean; executing: boolean;
}) {
  return (
    <header className="glass-header sticky top-0 z-10">
      <div style={{
        maxWidth: "82rem",
        margin: "0 auto",
        padding: "0.875rem 1.75rem",
        display: "flex",
        flexWrap: "wrap" as const,
        alignItems: "center",
        justifyContent: "space-between",
        gap: "1rem",
      }}>
        {/* Brand */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <a
            href="/"
            style={{
              color: T.white,
              textDecoration: "none",
              display: "flex",
              alignItems: "center",
              transition: "opacity 0.15s",
            }}
            onMouseEnter={(e) => ((e.currentTarget as HTMLElement).style.opacity = "0.7")}
            onMouseLeave={(e) => ((e.currentTarget as HTMLElement).style.opacity = "1")}
          >
            <span style={{ fontFamily: "'Kola', sans-serif", fontSize: "1.75rem", letterSpacing: "0.04em", textTransform: "uppercase" }}>ARBITER</span>
          </a>
          <span style={{
            fontFamily: T.poppins,
            fontSize: "0.62rem",
            fontWeight: 500,
            display: "flex",
            alignItems: "center",
            gap: "0.35rem",
            background: "rgba(255,255,255,0.05)",
            border: "1px solid rgba(255,255,255,0.09)",
            borderRadius: "999px",
            padding: "0.18rem 0.65rem",
            color: T.grayDim,
          }}>
            <span style={{ width: 5, height: 5, borderRadius: "50%", background: T.green, flexShrink: 0 }} />
            Razorpay Test Mode
          </span>
        </div>

        {/* Buttons */}
        <div style={{ display: "flex", flexWrap: "wrap" as const, alignItems: "center", gap: "0.5rem" }}>
          {/* Primary — solid orange */}
          <button
            onClick={onExecutePending}
            disabled={executing || loading}
            className="btn-primary"
            style={{ display: "flex", alignItems: "center", gap: "0.4rem", padding: "0.5rem 1rem", fontSize: "0.75rem" }}
          >
            <span className={executing ? "animate-spin" : ""}>💳</span>
            {executing ? "Executing…" : "Execute Pending Actions"}
          </button>

          {/* Secondary — glass */}
          <button
            onClick={onProcessDue}
            disabled={executing || loading}
            className="btn-glass"
            style={{ display: "flex", alignItems: "center", gap: "0.4rem", padding: "0.5rem 0.875rem", fontSize: "0.75rem", fontWeight: 500 }}
          >
            <span>⏰</span> Process Due Actions
          </button>

          <button
            onClick={onProcessAI}
            disabled={aiProcessing || loading}
            className="btn-glass-ai"
            style={{ display: "flex", alignItems: "center", gap: "0.4rem", padding: "0.5rem 0.875rem", fontSize: "0.75rem", fontWeight: 600 }}
          >
            <span className={aiProcessing ? "animate-spin" : ""}>🤖</span>
            {aiProcessing ? "Running AI…" : "Run AI Reasoning"}
          </button>

          <button
            onClick={onRefresh}
            disabled={loading}
            className="btn-glass"
            style={{ display: "flex", alignItems: "center", gap: "0.4rem", padding: "0.5rem 0.875rem", fontSize: "0.75rem", fontWeight: 500 }}
          >
            <span className={loading ? "animate-spin" : ""}>🔄</span> Refresh
          </button>
        </div>
      </div>
    </header>
  );
}

// ── Main Dashboard Page ───────────────────────────────────────────────────────
export default function DashboardPage() {
  const [summary, setSummary]     = useState<SummaryData | null>(null);
  const [events, setEvents]       = useState<EventItem[]>([]);
  const [loading, setLoading]     = useState(true);
  const [aiProcessing, setAIP]    = useState(false);
  const [executing, setExecuting] = useState(false);
  const [error, setError]         = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const [sR, eR] = await Promise.all([
        fetch(`${API_BASE_URL}/dashboard/summary`),
        fetch(`${API_BASE_URL}/dashboard/events`),
      ]);
      if (!sR.ok || !eR.ok) throw new Error("Failed to fetch dashboard data");
      setSummary(await sR.json());
      setEvents(await eR.json());
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Failed to load dashboard data");
    } finally { setLoading(false); }
  }, []);

  const handleProcessAI = async () => {
    setAIP(true);
    try { const r = await fetch(`${API_BASE_URL}/events/process-ai`, { method: "POST" }); if (r.ok) await fetchData(); }
    catch (e) { console.error(e); } finally { setAIP(false); }
  };
  const handleExecutePending = async () => {
    setExecuting(true);
    try { const r = await fetch(`${API_BASE_URL}/actions/execute-pending`, { method: "POST" }); if (r.ok) await fetchData(); }
    catch (e) { console.error(e); } finally { setExecuting(false); }
  };
  const handleProcessDue = async () => {
    setExecuting(true);
    try { const r = await fetch(`${API_BASE_URL}/actions/process-due`, { method: "POST" }); if (r.ok) await fetchData(); }
    catch (e) { console.error(e); } finally { setExecuting(false); }
  };

  useEffect(() => { fetchData(); }, [fetchData]);

  const aiAgreed = summary?.ai_agreement_count ?? 0;
  const totalAI  = summary?.total_ai_classified ?? 0;

  return (
    <div style={{ position: "relative", minHeight: "100dvh", overflowX: "hidden" }}>
      {/* Fixed pitch-black + orange glow background */}
      <BackgroundLayer />

      <Header
        onRefresh={fetchData} onProcessAI={handleProcessAI}
        onExecutePending={handleExecutePending} onProcessDue={handleProcessDue}
        loading={loading} aiProcessing={aiProcessing} executing={executing}
      />

      <main style={{
        position: "relative",
        zIndex: 1,
        maxWidth: "82rem",
        margin: "0 auto",
        padding: "2rem 1.75rem",
        display: "flex",
        flexDirection: "column" as const,
        gap: "1.75rem",
      }}>
        {/* Page title */}
        <div style={{ display: "flex", flexWrap: "wrap" as const, alignItems: "center", justifyContent: "space-between", gap: "1rem" }}>
          <div>
            <h1 style={{ fontFamily: T.poppins, fontSize: "1.5rem", fontWeight: 700, color: T.white, margin: 0, letterSpacing: "-0.025em" }}>
              Overview
            </h1>
            <p style={{ fontFamily: T.poppins, fontSize: "0.78rem", color: T.grayDim, margin: "0.25rem 0 0" }}>
              Live Razorpay test mode actions &amp; side-by-side Rules vs. AI evaluation.
            </p>
          </div>

          {totalAI > 0 && (
            <div className="glass-panel" style={{ padding: "0.45rem 1rem", display: "flex", alignItems: "center", gap: "0.5rem", borderRadius: "999px" }}>
              <span style={{ fontFamily: T.poppins, fontSize: "0.68rem", fontWeight: 700, color: T.orange }}>🤖 AI Alignment:</span>
              <span style={{ fontFamily: T.poppins, fontSize: "0.68rem", color: T.gray }}>
                Agreed with rules engine on {aiAgreed}/{totalAI} events
              </span>
            </div>
          )}
        </div>

        {/* Error */}
        {error && (
          <div style={{ padding: "0.875rem 1.125rem", background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.22)", borderRadius: "12px", fontSize: "0.78rem", fontFamily: T.poppins, color: T.red, display: "flex", alignItems: "center", justifyContent: "space-between", gap: "1rem" }}>
            <span>Unable to connect to backend API ({API_BASE_URL}). Make sure the backend server is running.</span>
            <button onClick={fetchData} style={{ fontWeight: 700, textDecoration: "underline", background: "none", border: "none", color: "inherit", cursor: "pointer", flexShrink: 0 }}>Retry</button>
          </div>
        )}

        {/* Stat cards */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "1.25rem" }}>
          <StatCard
            label="Revenue Recovered (Without Agent)"
            value={summary?.revenue_recovered_without_agent_formatted || "₹0"}
            subtitle="Baseline — no recovery agent active"
            variant="neutral"
            loading={loading}
          />
          <StatCard
            label="Revenue Recovered (With Agent)"
            value={summary?.revenue_recovered_with_agent_formatted || "₹0"}
            subtitle={summary ? `${summary.total_events} events · ${totalAI} AI analyzed` : "Active AI pipeline"}
            variant="accent"
            loading={loading}
          />
        </div>

        {/* Events table */}
        <EventsTable events={events} loading={loading} />
      </main>
    </div>
  );
}

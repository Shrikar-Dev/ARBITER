import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx,mdx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      // ── Color tokens ─────────────────────────────────────────────────────
      // All colors are defined here as CSS-variable-backed tokens so every
      // component uses semantic names. To retheme the entire dashboard,
      // change these values (or swap the CSS variables in globals.css).
      colors: {
        // Base surfaces
        bg: {
          base:    "rgb(var(--color-bg-base)    / <alpha-value>)",
          raised:  "rgb(var(--color-bg-raised)  / <alpha-value>)",
          sunken:  "rgb(var(--color-bg-sunken)  / <alpha-value>)",
          overlay: "rgb(var(--color-bg-overlay) / <alpha-value>)",
        },
        // Content / text
        content: {
          primary:   "rgb(var(--color-content-primary)   / <alpha-value>)",
          secondary: "rgb(var(--color-content-secondary) / <alpha-value>)",
          muted:     "rgb(var(--color-content-muted)     / <alpha-value>)",
        },
        // Accent — warm amber/gold; change one variable to re-accent
        accent: {
          DEFAULT: "rgb(var(--color-accent)        / <alpha-value>)",
          dim:     "rgb(var(--color-accent-dim)    / <alpha-value>)",
          muted:   "rgb(var(--color-accent-muted)  / <alpha-value>)",
        },
        // Semantic state colors
        success: "rgb(var(--color-success) / <alpha-value>)",
        warning: "rgb(var(--color-warning) / <alpha-value>)",
        danger:  "rgb(var(--color-danger)  / <alpha-value>)",
        // Borders
        border: {
          DEFAULT: "rgb(var(--color-border)       / <alpha-value>)",
          subtle:  "rgb(var(--color-border-subtle) / <alpha-value>)",
        },
      },
      // ── Typography ───────────────────────────────────────────────────────
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Menlo", "monospace"],
      },
      fontSize: {
        // Tighter scale ratio (1.2) suited to dense product UIs
        "2xs": ["0.625rem", { lineHeight: "0.875rem" }],
        xs:   ["0.75rem",  { lineHeight: "1rem"     }],
        sm:   ["0.875rem", { lineHeight: "1.25rem"  }],
        base: ["1rem",     { lineHeight: "1.5rem"   }],
        lg:   ["1.125rem", { lineHeight: "1.75rem"  }],
        xl:   ["1.25rem",  { lineHeight: "1.75rem"  }],
        "2xl":["1.5rem",   { lineHeight: "2rem"     }],
        "3xl":["1.875rem", { lineHeight: "2.25rem"  }],
      },
      // ── Spacing rhythm ───────────────────────────────────────────────────
      spacing: {
        "4.5": "1.125rem",
        "13":  "3.25rem",
        "18":  "4.5rem",
      },
      // ── Box shadows ──────────────────────────────────────────────────────
      // Legacy utility shadows kept for compatibility.
      // Neomorphic shadows live as CSS custom properties in globals.css
      // and are applied via .neo-* component classes.
      boxShadow: {
        card:         "0 1px 3px 0 rgb(0 0 0 / 0.4), 0 1px 2px -1px rgb(0 0 0 / 0.3)",
        "card-hover": "0 4px 12px 0 rgb(0 0 0 / 0.55), 0 2px 4px -2px rgb(0 0 0 / 0.4)",
        glow:         "0 0 20px 2px rgb(var(--color-accent) / 0.18)",
        // Neomorphic presets (also available as .neo-* CSS classes)
        "neo-raised": "6px 6px 14px rgba(0,0,0,0.75), -6px -6px 14px rgba(255,255,255,0.055)",
        "neo-inset":  "inset 4px 4px 10px rgba(0,0,0,0.75), inset -4px -4px 10px rgba(255,255,255,0.055)",
        "neo-flat":   "2px 2px 5px rgba(0,0,0,0.75), -2px -2px 5px rgba(255,255,255,0.055)",
      },
      // ── Border radius ────────────────────────────────────────────────────
      borderRadius: {
        card: "0.75rem",
      },
      // ── Animation ────────────────────────────────────────────────────────
      transitionTimingFunction: {
        "out-expo": "cubic-bezier(0.16, 1, 0.3, 1)",
      },
      transitionDuration: {
        "200": "200ms",
        "250": "250ms",
      },
    },
  },
  plugins: [],
};

export default config;

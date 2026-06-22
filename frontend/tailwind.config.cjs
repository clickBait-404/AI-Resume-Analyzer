/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#FAFAF8",
        ink: "#13151A",
        slate: "#71717A",
        "slate-light": "#A1A1AA",
        line: "#E4E4E1",
        accent: "#2563EB",
        "accent-dim": "#DBE5FD",
        match: "#059669",
        "match-dim": "#D1FAE5",
        gap: "#DC2626",
        "gap-dim": "#FEE2E2",
        amber: "#D97706",
        "amber-dim": "#FEF3C7",
      },
      fontFamily: {
        display: ["Fraunces", "ui-serif", "Georgia", "serif"],
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      fontSize: {
        "hero": ["clamp(2.75rem, 5vw, 4.75rem)", { lineHeight: "1.02", letterSpacing: "-0.02em" }],
      },
      borderRadius: {
        sm: "6px",
        DEFAULT: "10px",
        lg: "14px",
        xl: "20px",
      },
      boxShadow: {
        card: "0 1px 2px rgba(19,21,26,0.04), 0 1px 1px rgba(19,21,26,0.03)",
        "card-hover": "0 4px 16px rgba(19,21,26,0.08)",
      },
      animation: {
        "scan": "scan 2.8s ease-in-out infinite",
        "fade-up": "fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards",
      },
      keyframes: {
        scan: {
          "0%, 100%": { transform: "translateY(0%)" },
          "50%": { transform: "translateY(calc(100% - 2px))" },
        },
        fadeUp: {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};

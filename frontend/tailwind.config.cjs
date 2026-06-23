/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#F8FAFC",

        ink: "#0F172A",

        slate: "#64748B",

        "slate-light": "#94A3B8",

        line: "#E2E8F0",

        accent: "#2563EB",

        "accent-dim": "#DBEAFE",

        secondary: "#7C3AED",

        match: "#10B981",

        "match-dim": "#D1FAE5",

        gap: "#EF4444",

        "gap-dim": "#FEE2E2",

        amber: "#F59E0B",

        "amber-dim": "#FEF3C7",
      },

      fontFamily: {
        display: ["Inter", "ui-sans-serif", "system-ui"],
        sans: ["Inter", "ui-sans-serif", "system-ui"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },

      fontSize: {
        hero: [
          "clamp(3.5rem, 6vw, 5.5rem)",
          {
            lineHeight: "0.95",
            letterSpacing: "-0.04em",
          },
        ],
      },

      borderRadius: {
        sm: "8px",
        DEFAULT: "14px",
        lg: "20px",
        xl: "28px",
        "2xl": "32px",
        "3xl": "36px",
      },

      boxShadow: {
        card: "0 10px 30px rgba(15,23,42,.08)",

        "card-hover": "0 20px 50px rgba(15,23,42,.12)",

        glow: "0 20px 50px rgba(37,99,235,.15)",

        glass: "0 8px 32px rgba(15,23,42,.08)",
      },

      animation: {
        scan: "scan 3s ease-in-out infinite",

        "fade-up": "fadeUp .6s cubic-bezier(.16,1,.3,1) forwards",

        float: "float 5s ease-in-out infinite",

        pulseGlow: "pulseGlow 3s ease-in-out infinite",
      },

      keyframes: {
        scan: {
          "0%,100%": {
            transform: "translateY(0%)",
          },

          "50%": {
            transform: "translateY(calc(100% - 2px))",
          },
        },

        fadeUp: {
          "0%": {
            opacity: "0",
            transform: "translateY(12px)",
          },

          "100%": {
            opacity: "1",
            transform: "translateY(0)",
          },
        },

        float: {
          "0%,100%": {
            transform: "translateY(0px)",
          },

          "50%": {
            transform: "translateY(-8px)",
          },
        },

        pulseGlow: {
          "0%,100%": {
            boxShadow: "0 0 0 rgba(37,99,235,.15)",
          },

          "50%": {
            boxShadow: "0 0 30px rgba(37,99,235,.25)",
          },
        },
      },
    },
  },
  plugins: [],
};

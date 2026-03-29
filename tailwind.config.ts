import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        void: "#09090B",
        surface: "#18181B",
        line: "#27272A",
        kengo: {
          DEFAULT: "#3B82F6",
          light: "#60A5FA",
        },
        success: "#10B981",
        amber: "#F59E0B",
        muted: "#6B7280",
        error: "#EF4444",
        light: {
          bg: "#FAFAFA",
          surface: "#F4F4F5",
          border: "#E4E4E7",
        },
        text: {
          primary: "#FAFAFA",
          secondary: "#A1A1AA",
          "primary-light": "#09090B",
          "secondary-light": "#52525B",
        },
      },
      fontFamily: {
        display: [
          "var(--font-display)",
          "system-ui",
          "-apple-system",
          "sans-serif",
        ],
        sans: [
          "var(--font-sans)",
          "system-ui",
          "-apple-system",
          "sans-serif",
        ],
        mono: [
          "var(--font-mono)",
          "ui-monospace",
          "SFMono-Regular",
          "monospace",
        ],
      },
      maxWidth: {
        page: "1280px",
      },
      borderRadius: {
        "2xl": "16px",
        xl: "12px",
      },
      animation: {
        "pulse-live": "pulseLive 2s ease-in-out infinite",
        "count-up": "countUp 1.2s ease-out forwards",
        "fade-up": "fadeUp 600ms cubic-bezier(0.22, 1, 0.36, 1) forwards",
      },
      keyframes: {
        pulseLive: {
          "0%, 100%": { opacity: "0.5" },
          "50%": { opacity: "1" },
        },
        fadeUp: {
          "0%": { opacity: "0", transform: "translateY(30px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};
export default config;

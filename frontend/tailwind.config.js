/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#0B1526",
          900: "#0F1B2D",
          800: "#16263D",
          700: "#1F344F",
          600: "#2C4568",
        },
        paper: {
          DEFAULT: "#F6F4EE",
          100: "#FBFAF6",
          200: "#EFEBE0",
        },
        slate: {
          50: "#F3F4F3",
          100: "#E4E6E4",
          300: "#A7ADB4",
          500: "#5C6670",
          600: "#3D4B5C",
          700: "#2C3743",
        },
        ochre: {
          50: "#FBF1E1",
          100: "#F3DDAE",
          400: "#D69A32",
          500: "#C17817",
          600: "#9B5F10",
        },
        rust: {
          50: "#FBE9E5",
          400: "#C6532F",
          500: "#B3311D",
          600: "#8E2516",
        },
        moss: {
          50: "#E7EEE5",
          400: "#4C8863",
          500: "#2F6844",
          600: "#235034",
        },
      },
      fontFamily: {
        serif: ["\"Source Serif 4\"", "Georgia", "serif"],
        sans: ["\"Inter\"", "system-ui", "sans-serif"],
        mono: ["\"IBM Plex Mono\"", "ui-monospace", "monospace"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(15, 27, 45, 0.06)",
        panel: "0 2px 10px rgba(15, 27, 45, 0.08)",
      },
      borderRadius: {
        sm: "3px",
        DEFAULT: "4px",
        md: "6px",
      },
    },
  },
  plugins: [],
};

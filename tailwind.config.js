/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["'Playfair Display'", "Georgia", "serif"],
        mono: ["'IBM Plex Mono'", "'SF Mono'", "Consolas", "monospace"],
      },
      colors: {
        paper: "#f6f3ee",
        paperCard: "#fcfbf9",
        ink: "#2a2521",
        inkSoft: "#6b6259",
        inkFaint: "#8c8379",
        rule: "#d9d2c7",
        crimson: "#a3222f",
        crimsonDim: "rgba(163, 34, 47, 0.08)",
        gold: "#b58a3d",
        matched: "#3f7a4e",
        matchedDim: "rgba(63, 122, 78, 0.12)",
        pending: "#a8752f",
        pendingDim: "rgba(168, 117, 47, 0.14)",
        exception: "#b03a2e",
        exceptionDim: "rgba(176, 58, 46, 0.1)",
      },
    },
  },
  plugins: [],
};

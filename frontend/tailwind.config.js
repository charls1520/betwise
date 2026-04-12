/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "outline": "#687690",
        "tertiary": "#47c4ff",
        "surface-variant": "#102645",
        "outline-variant": "#3b4861",
        "surface-container-high": "#0b203d",
        "on-surface": "#dbe6ff",
        "primary-container": "#0abc56",
        "background": "#010e24",
        "surface-bright": "#152c4e",
        "primary": "#6bff8f",
        "on-surface-variant": "#9eabc8",
        "surface-container-low": "#02132b",
        "surface-container": "#061934",
      },
      fontFamily: {
        headline: ["Space Grotesk", "sans-serif"],
        body: ["Manrope", "sans-serif"],
      }
    },
  },
  plugins: [],
}
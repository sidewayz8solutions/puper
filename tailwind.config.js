/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#your-color-here',  // Define your custom colors
          100: '#your-color-here',
          // ... add more shades as needed
        }
      }
    },
  },
  plugins: [],
}
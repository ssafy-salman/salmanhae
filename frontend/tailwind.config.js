/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          light: '#E8F8F5',
          DEFAULT: '#1ABC9C',
          dark: '#16A085'
        },
        danger: '#E74C3C',
        warning: '#E67E22',
        info: '#3498DB'
      }
    },
  },
  plugins: [],
}
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0fdf4',
          100: '#dcfce7',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
        },
        assay: {
          bg: '#0B0F17',
          card: '#131B2B',
          border: '#1F2E47',
          accent: '#3B82F6',
          warning: '#F59E0B',
          danger: '#EF4444',
          success: '#10B981',
          text: '#F3F4F6',
          muted: '#9CA3AF'
        }
      },
      fontFamily: {
        mono: ['Geist Mono', 'Menlo', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}

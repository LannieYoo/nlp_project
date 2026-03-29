/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      colors: {
        /* Refined light palette — warm white / cool pearl */
        surface: {
          50:  '#ffffff',
          100: '#f8f8f8',
          200: '#f0f0f0',
          300: '#e8e8e8',
          400: '#d4d4d4',
          500: '#a3a3a3',
          600: '#737373',
          700: '#525252',
          800: '#2e2e2e',
          900: '#1a1a1a',
          950: '#0c0c0c',
        },
        /* Steel-slate accent — sophisticated, NOT green */
        accent: {
          50:  '#f0f4ff',
          100: '#e0e9ff',
          200: '#c7d8ff',
          300: '#a5beff',
          400: '#7b9ef7',
          500: '#5273e8',
          600: '#3d56d4',
          700: '#3145b8',
          800: '#2a3a96',
          900: '#273278',
        },
      },
      boxShadow: {
        'soft': '0 1px 3px rgba(0,0,0,0.06), 0 2px 12px rgba(0,0,0,0.04)',
        'medium': '0 2px 8px rgba(0,0,0,0.08), 0 8px 24px rgba(0,0,0,0.06)',
        'card': '0 1px 2px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.04)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.35s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(6px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}

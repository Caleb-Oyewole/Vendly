/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        // Map everything to the CSS variables
        white: 'var(--color-white)',
        brand: { DEFAULT: 'var(--color-brand)', tint: 'var(--color-brand-tint)' },
        ink: 'var(--color-ink)',
        muted: 'var(--color-muted)',
        line: 'var(--color-line)',
        surface: 'var(--color-surface)',
        accent: '#F59E0B',
        
        // Hijack the specific slate colors we used for hovers and progress bars
        slate: {
          50: 'var(--color-slate-50)',
          100: 'var(--color-slate-100)',
        },
        
        // Keep status colors static (green should always be green)
        status: {
          confirmed: '#16A34A',
          awaiting: '#2563EB',
          declined: '#DC2626',
          failed: '#EA580C',
          idle: '#94A3B8'
        }
      },
      borderRadius: {
        'card': '12px',
        'input': '8px',
        'btn': '8px',
        'badge': '9999px',
      }
    },
  },
  plugins: [],
}
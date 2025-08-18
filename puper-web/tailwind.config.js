/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Brown-based palette (main brand colors)
        primary: {
          50: '#fdf8f6',   // Lightest cream
          100: '#f2e8e5',  // Light beige
          200: '#eaddd7',  // Soft tan
          300: '#e0cec7',  // Light brown
          400: '#d2bab0',  // Medium tan
          500: '#bfa094',  // Warm brown
          600: '#a18072',  // Medium brown (used in logo)
          700: '#8b6f61',  // Main brown (logo primary)
          800: '#73624a',  // Deep brown
          900: '#5d4e3a',  // Darkest brown
          950: '#2f2419',  // Almost black brown
        },
        
        // Psychedelic accent colors
        'psychedelic-purple': '#8B5CF6',
        'psychedelic-pink': '#EC4899',
        'psychedelic-orange': '#F97316',
        'psychedelic-lime': '#84CC16',
        'psychedelic-cyan': '#06B6D4',
        'psychedelic-yellow': '#EAB308',
        
        // Semantic colors
        success: '#22C55E',
        warning: '#F59E0B',
        error: '#EF4444',
        info: '#0EA5E9',
        
        // Neutral grays with cool tint
        gray: {
          50: '#F8FAFC',
          100: '#F1F5F9',
          200: '#E2E8F0',
          300: '#CBD5E1',
          400: '#94A3B8',
          500: '#64748B',
          600: '#475569',
          700: '#334155',
          800: '#1E293B',
          900: '#0F172A',
          950: '#020617',
        }
      },
      
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        display: ['Poppins', 'system-ui', 'sans-serif'],
      },
      
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'slide-left': 'slideLeft 0.3s ease-out',
        'slide-right': 'slideRight 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'gradient': 'gradient 8s ease infinite',
        'spin-slow': 'spin 3s linear infinite',
        'bounce-gentle': 'bounceGentle 2s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite',
        'wave': 'wave 2s ease-in-out infinite',
        'ripple': 'ripple 1s cubic-bezier(0, 0, 0.2, 1) infinite',
      },
      
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideLeft: {
          '0%': { transform: 'translateX(10px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideRight: {
          '0%': { transform: 'translateX(-10px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        gradient: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        bounceGentle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        },
        glow: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(59, 127, 166, 0.3)' },
          '50%': { boxShadow: '0 0 30px rgba(59, 127, 166, 0.5)' },
        },
        wave: {
          '0%, 100%': { transform: 'rotate(-3deg)' },
          '50%': { transform: 'rotate(3deg)' },
        },
        ripple: {
          '0%': { transform: 'scale(0.8)', opacity: '1' },
          '100%': { transform: 'scale(2.4)', opacity: '0' },
        }
      },
      
      boxShadow: {
        'glow': '0 0 20px rgba(139, 92, 246, 0.3)',
        'glow-pink': '0 0 20px rgba(236, 72, 153, 0.3)',
        'glow-strong': '0 0 30px rgba(236, 72, 153, 0.5)',
        'glow-brown': '0 0 20px rgba(161, 128, 114, 0.3)',
        'inner-glow': 'inset 0 0 20px rgba(139, 92, 246, 0.2)',
        'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.15)',
        'glass-dark': '0 8px 32px 0 rgba(93, 78, 58, 0.2)',
        'elevation-1': '0 2px 4px rgba(93, 78, 58, 0.1)',
        'elevation-2': '0 4px 8px rgba(93, 78, 58, 0.12)',
        'elevation-3': '0 8px 16px rgba(93, 78, 58, 0.15)',
        'elevation-4': '0 16px 32px rgba(93, 78, 58, 0.18)',
        'card': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      },
      
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'gradient-blue': 'linear-gradient(135deg, #3B7FA6 0%, #336e91 50%, #2a5a78 100%)',
        'gradient-ocean': 'linear-gradient(135deg, #0EA5E9 0%, #3B7FA6 50%, #6366F1 100%)',
        'gradient-sunset': 'linear-gradient(135deg, #F97316 0%, #EC4899 50%, #8B5CF6 100%)',
        'gradient-fresh': 'linear-gradient(135deg, #22C55E 0%, #14B8A6 50%, #0EA5E9 100%)',
        'gradient-warm': 'linear-gradient(135deg, #fef3c7 0%, #fed7aa 50%, #fce7f3 100%)',
      },
      
      screens: {
        'xs': '475px',
      },
      
      transitionDelay: {
        '2000': '2000ms',
        '3000': '3000ms',
        '4000': '4000ms',
      },
      
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms')({
      strategy: 'class',
    }),
    require('@tailwindcss/typography'),
  ],
}
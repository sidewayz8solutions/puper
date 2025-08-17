import React from 'react';
import { motion } from 'framer-motion';

interface PuperLogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showText?: boolean;
  className?: string;
  animated?: boolean;
  variant?: 'default' | 'psychedelic' | 'minimal';
}

const PuperLogo: React.FC<PuperLogoProps> = ({ 
  size = 'md', 
  showText = true, 
  className = '',
  animated = true,
  variant = 'default'
}) => {
  const sizes = {
    sm: { icon: 32, text: 'text-xl' },
    md: { icon: 48, text: 'text-2xl' },
    lg: { icon: 64, text: 'text-4xl' },
    xl: { icon: 96, text: 'text-5xl' }
  };

  const currentSize = sizes[size];

  const iconVariants = {
    initial: { scale: 1, rotate: 0 },
    hover: { 
      scale: 1.05, 
      rotate: [0, -3, 3, -3, 0],
      transition: { duration: 0.5 }
    },
    tap: { scale: 0.95 }
  };

  const floatVariants = {
    initial: { y: 0 },
    animate: {
      y: [-3, 3, -3],
      transition: {
        duration: 4,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  };

  return (
    <motion.div 
      className={`flex items-center space-x-3 ${className}`}
      whileHover="hover"
      whileTap="tap"
      initial="initial"
      animate={animated ? "animate" : "initial"}
    >
      {/* Location Pin with Toilet Paper Icon */}
      <motion.div
        variants={animated ? iconVariants : {}}
        className="relative"
      >
        <motion.svg 
          width={currentSize.icon} 
          height={currentSize.icon * 1.2} 
          viewBox="0 0 80 96" 
          fill="none"
          variants={animated ? floatVariants : {}}
          className="drop-shadow-lg"
        >
          <defs>
            {/* Brown gradient for default */}
            <linearGradient id="brownGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#8b6f61" />
              <stop offset="50%" stopColor="#73624a" />
              <stop offset="100%" stopColor="#5d4e3a" />
            </linearGradient>
            
            {/* Psychedelic gradient */}
            <linearGradient id="psychedelicGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#8B5CF6">
                <animate attributeName="stop-color" 
                  values="#8B5CF6;#EC4899;#F97316;#8B5CF6" 
                  dur="3s" 
                  repeatCount="indefinite" />
              </stop>
              <stop offset="50%" stopColor="#EC4899">
                <animate attributeName="stop-color" 
                  values="#EC4899;#F97316;#84CC16;#EC4899" 
                  dur="3s" 
                  repeatCount="indefinite" />
              </stop>
              <stop offset="100%" stopColor="#F97316">
                <animate attributeName="stop-color" 
                  values="#F97316;#84CC16;#06B6D4;#F97316" 
                  dur="3s" 
                  repeatCount="indefinite" />
              </stop>
            </linearGradient>

            {/* Inner shadow for depth */}
            <filter id="innerShadow">
              <feGaussianBlur in="SourceGraphic" stdDeviation="2"/>
              <feOffset dx="0" dy="2" result="offsetblur"/>
              <feFlood floodColor="#000000" floodOpacity="0.2"/>
              <feComposite in2="offsetblur" operator="in"/>
              <feMerge>
                <feMergeNode/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>

            {/* Glow effect */}
            <filter id="glow">
              <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          
          {/* Location pin shape */}
          <path 
            d="M40 0C17.909 0 0 17.909 0 40C0 52 8 62 12 68L40 96L68 68C72 62 80 52 80 40C80 17.909 62.091 0 40 0Z" 
            fill={variant === 'psychedelic' ? "url(#psychedelicGradient)" : "url(#brownGradient)"}
            filter={animated ? "url(#glow)" : ""}
          />
          
          {/* Inner circle background */}
          <circle 
            cx="40" 
            cy="38" 
            r="28" 
            fill="white"
            opacity="0.95"
          />
          
          {/* Toilet paper roll */}
          <g transform="translate(40, 38)">
            {/* Main roll */}
            <rect 
              x="-16" 
              y="-14" 
              width="32" 
              height="20" 
              rx="4" 
              fill={variant === 'psychedelic' ? "url(#psychedelicGradient)" : "#a18072"}
              opacity="0.9"
            />
            
            {/* Inner tube */}
            <ellipse 
              cx="0" 
              cy="-4" 
              rx="8" 
              ry="10" 
              fill="white"
              opacity="0.8"
            />
            
            {/* Perforated line */}
            <g stroke={variant === 'psychedelic' ? "#8B5CF6" : "#73624a"} strokeWidth="2" strokeDasharray="3 2" opacity="0.6">
              <line x1="-10" y1="0" x2="10" y2="0" />
            </g>
            
            {/* Paper hanging down with wave effect */}
            <path 
              d="M -8 6 Q -6 10, -4 8 T 0 10 T 4 8 T 8 10 L 8 14 L -8 14 Z" 
              fill="white"
              opacity="0.7"
              stroke={variant === 'psychedelic' ? "#EC4899" : "#d2bab0"}
              strokeWidth="0.5"
            />
          </g>
          
          {/* Shine effect for depth */}
          <ellipse 
            cx="28" 
            cy="28" 
            rx="12" 
            ry="16" 
            fill="white"
            opacity="0.2"
          />

          {/* Psychedelic sparkles */}
          {variant === 'psychedelic' && animated && (
            <>
              <motion.circle
                cx="20"
                cy="20"
                r="2"
                fill="#EAB308"
                animate={{
                  opacity: [0, 1, 0],
                  scale: [0, 1.5, 0],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  delay: 0,
                }}
              />
              <motion.circle
                cx="60"
                cy="25"
                r="2"
                fill="#06B6D4"
                animate={{
                  opacity: [0, 1, 0],
                  scale: [0, 1.5, 0],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  delay: 0.5,
                }}
              />
              <motion.circle
                cx="55"
                cy="50"
                r="2"
                fill="#84CC16"
                animate={{
                  opacity: [0, 1, 0],
                  scale: [0, 1.5, 0],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  delay: 1,
                }}
              />
            </>
          )}
        </motion.svg>
      </motion.div>
      
      {/* Text with umlaut */}
      {showText && (
        <motion.div 
          className={`font-display font-bold ${currentSize.text} select-none`}
          initial={{ opacity: 1 }}
          whileHover={{ 
            scale: 1.02,
            transition: { duration: 0.2 }
          }}
        >
          {variant === 'psychedelic' ? (
            <span className="text-gradient">püper</span>
          ) : (
            <span 
              style={{
                background: 'linear-gradient(135deg, #8b6f61 0%, #73624a 50%, #5d4e3a 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                color: 'transparent',
              }}
            >
              püper
            </span>
          )}
        </motion.div>
      )}

      {/* Optional badge for new features */}
      {variant === 'psychedelic' && (
        <motion.div
          className="absolute -top-1 -right-1"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.5, type: "spring" }}
        >
          <span className="px-2 py-1 text-xs font-bold text-white bg-gradient-to-r from-psychedelic-purple to-psychedelic-pink rounded-full">
            NEW
          </span>
        </motion.div>
      )}
    </motion.div>
  );
};

// Mini version for favicon/small spaces
export const PuperIcon: React.FC<{ size?: number; className?: string }> = ({ 
  size = 24, 
  className = '' 
}) => {
  return (
    <svg 
      width={size} 
      height={size * 1.2} 
      viewBox="0 0 80 96" 
      fill="none"
      className={className}
    >
      <defs>
        <linearGradient id="iconGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#8b6f61" />
          <stop offset="100%" stopColor="#5d4e3a" />
        </linearGradient>
      </defs>
      
      <path 
        d="M40 0C17.909 0 0 17.909 0 40C0 52 8 62 12 68L40 96L68 68C72 62 80 52 80 40C80 17.909 62.091 0 40 0Z" 
        fill="url(#iconGradient)"
      />
      
      <circle cx="40" cy="38" r="28" fill="white" opacity="0.95" />
      
      <rect x="24" y="24" width="32" height="20" rx="4" fill="#a18072" opacity="0.9" />
      <ellipse cx="40" cy="34" rx="8" ry="10" fill="white" opacity="0.8" />
      <line x1="30" y1="38" x2="50" y2="38" stroke="#73624a" strokeWidth="2" strokeDasharray="3 2" opacity="0.6" />
      <path d="M 32 44 Q 34 48, 36 46 T 40 48 T 44 46 T 48 48 L 48 52 L 32 52 Z" fill="white" opacity="0.7" />
    </svg>
  );
};

export default PuperLogo;
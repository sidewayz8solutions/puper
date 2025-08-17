import React from 'react';

interface PuperLogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  showText?: boolean;
}

const PuperLogo: React.FC<PuperLogoProps> = ({ 
  size = 'md', 
  className = '', 
  showText = true 
}) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
    xl: 'w-24 h-24'
  };

  const textSizeClasses = {
    sm: 'text-lg',
    md: 'text-xl',
    lg: 'text-2xl',
    xl: 'text-4xl'
  };

  return (
    <div className={`flex items-center space-x-3 ${className}`}>
      {/* Logo Icon */}
      <div className={`${sizeClasses[size]} relative`}>
        <svg
          viewBox="0 0 200 200"
          className="w-full h-full"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Map Pin Background */}
          <path
            d="M100 20C70 20 45 45 45 75C45 105 100 180 100 180S155 105 155 75C155 45 130 20 100 20Z"
            fill="url(#brownGradient)"
            className="drop-shadow-lg"
          />
          
          {/* Toilet Paper Roll */}
          <g transform="translate(100, 75)">
            {/* Main roll body */}
            <rect
              x="-25"
              y="-20"
              width="50"
              height="35"
              rx="25"
              fill="white"
              className="drop-shadow-sm"
            />
            
            {/* Roll center hole */}
            <ellipse
              cx="-15"
              cy="0"
              rx="8"
              ry="12"
              fill="#8b6f61"
            />
            
            {/* Perforated lines */}
            <g stroke="#d2bab0" strokeWidth="2" strokeDasharray="3,2">
              <line x1="5" y1="-15" x2="25" y2="-15" />
              <line x1="5" y1="-5" x2="25" y2="-5" />
              <line x1="5" y1="5" x2="25" y2="5" />
            </g>
            
            {/* Hanging paper */}
            <path
              d="M20 15 L20 25 L15 30 L10 25 L5 30 L0 25 L0 15"
              fill="white"
              stroke="#d2bab0"
              strokeWidth="1"
            />
          </g>
          
          {/* Gradient Definitions */}
          <defs>
            <linearGradient id="brownGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#a18072" />
              <stop offset="50%" stopColor="#8b6f61" />
              <stop offset="100%" stopColor="#73624a" />
            </linearGradient>
          </defs>
        </svg>
      </div>
      
      {/* Logo Text */}
      {showText && (
        <span className={`font-display font-bold text-primary-800 ${textSizeClasses[size]}`}>
          puper
        </span>
      )}
    </div>
  );
};

export default PuperLogo;

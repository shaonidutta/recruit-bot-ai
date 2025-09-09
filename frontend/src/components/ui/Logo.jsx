import React from 'react';

/**
 * AI Recruitment Agent Logo Component
 * Modern, professional logo with AI and recruitment themes
 */
export const Logo = ({ 
  size = 'md', 
  variant = 'full', 
  className = '',
  showText = true 
}) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
    xl: 'w-24 h-24'
  };

  const textSizes = {
    sm: 'text-lg',
    md: 'text-xl',
    lg: 'text-2xl',
    xl: 'text-3xl'
  };

  const LogoIcon = () => (
    <div className={`${sizeClasses[size]} relative ${className}`}>
      <svg
        viewBox="0 0 100 100"
        className="w-full h-full"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Gradient Definitions */}
        <defs>
          <linearGradient id="primaryGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#3B82F6" />
            <stop offset="50%" stopColor="#8B5CF6" />
            <stop offset="100%" stopColor="#06B6D4" />
          </linearGradient>
          <linearGradient id="secondaryGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#10B981" />
            <stop offset="100%" stopColor="#059669" />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
            <feMerge> 
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>

        {/* Background Circle */}
        <circle
          cx="50"
          cy="50"
          r="45"
          fill="url(#primaryGradient)"
          className="drop-shadow-lg"
        />

        {/* AI Brain/Network Pattern */}
        <g className="opacity-90">
          {/* Central Node */}
          <circle cx="50" cy="50" r="8" fill="white" className="drop-shadow-sm" />
          
          {/* Network Nodes */}
          <circle cx="30" cy="35" r="4" fill="white" opacity="0.9" />
          <circle cx="70" cy="35" r="4" fill="white" opacity="0.9" />
          <circle cx="25" cy="65" r="4" fill="white" opacity="0.9" />
          <circle cx="75" cy="65" r="4" fill="white" opacity="0.9" />
          <circle cx="50" cy="25" r="3" fill="white" opacity="0.8" />
          <circle cx="50" cy="75" r="3" fill="white" opacity="0.8" />

          {/* Connection Lines */}
          <g stroke="white" strokeWidth="2" opacity="0.7" fill="none">
            <line x1="50" y1="50" x2="30" y2="35" />
            <line x1="50" y1="50" x2="70" y2="35" />
            <line x1="50" y1="50" x2="25" y2="65" />
            <line x1="50" y1="50" x2="75" y2="65" />
            <line x1="50" y1="50" x2="50" y2="25" />
            <line x1="50" y1="50" x2="50" y2="75" />
            <line x1="30" y1="35" x2="50" y2="25" />
            <line x1="70" y1="35" x2="50" y2="25" />
            <line x1="25" y1="65" x2="50" y2="75" />
            <line x1="75" y1="65" x2="50" y2="75" />
          </g>
        </g>

        {/* Recruitment Symbol (Magnifying Glass) */}
        <g transform="translate(65, 25)">
          <circle cx="0" cy="0" r="8" fill="none" stroke="white" strokeWidth="2.5" opacity="0.9" />
          <line x1="6" y1="6" x2="12" y2="12" stroke="white" strokeWidth="2.5" opacity="0.9" strokeLinecap="round" />
        </g>

        {/* AI Pulse Animation */}
        <circle cx="50" cy="50" r="35" fill="none" stroke="white" strokeWidth="1" opacity="0.3">
          <animate attributeName="r" values="35;40;35" dur="2s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="0.3;0.1;0.3" dur="2s" repeatCount="indefinite" />
        </circle>
      </svg>
    </div>
  );

  if (variant === 'icon') {
    return <LogoIcon />;
  }

  return (
    <div className={`flex items-center space-x-3 ${className}`}>
      <LogoIcon />
      {showText && (
        <div className="flex flex-col">
          <span className={`font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-cyan-600 bg-clip-text text-transparent ${textSizes[size]}`}>
            AI Recruit
          </span>
          <span className="text-xs text-gray-500 font-medium tracking-wide">
            INTELLIGENT HIRING
          </span>
        </div>
      )}
    </div>
  );
};

/**
 * Compact Logo for smaller spaces
 */
export const CompactLogo = ({ size = 'sm', className = '' }) => (
  <Logo 
    size={size} 
    variant="icon" 
    className={className}
    showText={false}
  />
);

/**
 * Full Logo with text for headers
 */
export const FullLogo = ({ size = 'md', className = '' }) => (
  <Logo 
    size={size} 
    variant="full" 
    className={className}
    showText={true}
  />
);

export default Logo;

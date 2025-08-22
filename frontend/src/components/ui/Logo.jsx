import React from 'react';
import { cn } from '../../utils/cn';

const Logo = ({ 
  size = 'default', 
  variant = 'full', 
  className,
  showText = true,
  ...props 
}) => {
  const sizeClasses = {
    sm: {
      icon: 'w-8 h-8',
      text: 'text-lg',
      subtitle: 'text-xs'
    },
    default: {
      icon: 'w-10 h-10',
      text: 'text-xl',
      subtitle: 'text-xs'
    },
    lg: {
      icon: 'w-12 h-12',
      text: 'text-2xl',
      subtitle: 'text-sm'
    },
    xl: {
      icon: 'w-16 h-16',
      text: 'text-3xl',
      subtitle: 'text-base'
    }
  };

  const currentSize = sizeClasses[size];

  const IconComponent = () => (
    <div className={cn(
      "bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105",
      currentSize.icon
    )}>
      {/* AI Icon with neural network pattern */}
      <div className="relative">
        <span className={cn(
          "text-white font-bold",
          size === 'sm' ? 'text-sm' : size === 'lg' ? 'text-xl' : size === 'xl' ? 'text-2xl' : 'text-lg'
        )}>
          AI
        </span>
        {/* Subtle circuit pattern overlay */}
        <div className="absolute inset-0 opacity-20">
          <svg viewBox="0 0 24 24" className="w-full h-full">
            <path
              d="M12 2L2 7v10c0 5.55 3.84 9.74 9 11 5.16-1.26 9-5.45 9-11V7l-10-5z"
              fill="none"
              stroke="currentColor"
              strokeWidth="0.5"
            />
            <circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" strokeWidth="0.5" />
            <path d="M12 1v6m0 10v6m11-11h-6m-10 0H1" stroke="currentColor" strokeWidth="0.3" />
          </svg>
        </div>
      </div>
    </div>
  );

  if (variant === 'icon') {
    return (
      <div className={cn("inline-flex", className)} {...props}>
        <IconComponent />
      </div>
    );
  }

  return (
    <div className={cn("flex items-center space-x-3", className)} {...props}>
      <IconComponent />
      {showText && (
        <div className="flex flex-col">
          <h1 className={cn(
            "font-bold text-gray-900 leading-tight",
            currentSize.text
          )}>
            AI Recruitment
          </h1>
          <p className={cn(
            "text-gray-500 -mt-1 leading-tight",
            currentSize.subtitle
          )}>
            Agent
          </p>
        </div>
      )}
    </div>
  );
};

// Alternative compact version
export const LogoCompact = ({ size = 'default', className, ...props }) => {
  const sizeClasses = {
    sm: { icon: 'w-8 h-8', text: 'text-lg' },
    default: { icon: 'w-10 h-10', text: 'text-xl' },
    lg: { icon: 'w-12 h-12', text: 'text-2xl' }
  };

  const currentSize = sizeClasses[size];

  return (
    <div className={cn("flex items-center space-x-2", className)} {...props}>
      <div className={cn(
        "bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center shadow-md",
        currentSize.icon
      )}>
        <span className={cn(
          "text-white font-bold",
          size === 'sm' ? 'text-sm' : size === 'lg' ? 'text-xl' : 'text-lg'
        )}>
          AI
        </span>
      </div>
      <span className={cn(
        "font-bold text-gray-900",
        currentSize.text
      )}>
        Recruitment
      </span>
    </div>
  );
};

// Brand mark only (just the icon)
export const BrandMark = ({ size = 'default', className, ...props }) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    default: 'w-10 h-10',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  };

  return (
    <div 
      className={cn(
        "bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105",
        sizeClasses[size],
        className
      )} 
      {...props}
    >
      <div className="relative">
        <span className={cn(
          "text-white font-bold",
          size === 'sm' ? 'text-sm' : size === 'lg' ? 'text-xl' : size === 'xl' ? 'text-2xl' : 'text-lg'
        )}>
          AI
        </span>
        {/* Neural network pattern */}
        <div className="absolute inset-0 opacity-20">
          <svg viewBox="0 0 24 24" className="w-full h-full">
            <circle cx="8" cy="8" r="1" fill="currentColor" />
            <circle cx="16" cy="8" r="1" fill="currentColor" />
            <circle cx="12" cy="16" r="1" fill="currentColor" />
            <path d="M8 8l4 8m0-8l-4 8m8-8l-4 8" stroke="currentColor" strokeWidth="0.3" />
          </svg>
        </div>
      </div>
    </div>
  );
};

export default Logo;

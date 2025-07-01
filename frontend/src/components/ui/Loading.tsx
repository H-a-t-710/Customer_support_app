import React from 'react';
import { cn } from '@/lib/utils';

export interface LoadingProps {
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'circle' | 'dots';
}

const Loading = ({ 
  className, 
  size = 'md',
  variant = 'circle'
}: LoadingProps) => {
  const sizeStyles = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  if (variant === 'dots') {
    return (
      <div className={cn('flex space-x-2 items-center justify-center', className)}>
        <div className={`animate-bounce bg-gray-500 rounded-full ${size === 'sm' ? 'h-2 w-2' : size === 'md' ? 'h-3 w-3' : 'h-4 w-4'}`} style={{ animationDelay: '0ms' }} />
        <div className={`animate-bounce bg-gray-500 rounded-full ${size === 'sm' ? 'h-2 w-2' : size === 'md' ? 'h-3 w-3' : 'h-4 w-4'}`} style={{ animationDelay: '150ms' }} />
        <div className={`animate-bounce bg-gray-500 rounded-full ${size === 'sm' ? 'h-2 w-2' : size === 'md' ? 'h-3 w-3' : 'h-4 w-4'}`} style={{ animationDelay: '300ms' }} />
      </div>
    );
  }

  return (
    <div className={cn('relative', className)}>
      <svg 
        className={cn('animate-spin text-gray-300', sizeStyles[size])} 
        xmlns="http://www.w3.org/2000/svg" 
        fill="none" 
        viewBox="0 0 24 24"
      >
        <circle 
          className="opacity-25" 
          cx="12" 
          cy="12" 
          r="10" 
          stroke="currentColor" 
          strokeWidth="4"
        ></circle>
        <path 
          className="opacity-75" 
          fill="currentColor" 
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        ></path>
      </svg>
    </div>
  );
};

export default Loading; 
import React from 'react';
import { cn } from '@/lib/utils';

export interface CardProps {
  className?: string;
  children: React.ReactNode;
}

export interface CardHeaderProps {
  className?: string;
  children: React.ReactNode;
}

export interface CardTitleProps {
  className?: string;
  children: React.ReactNode;
}

export interface CardDescriptionProps {
  className?: string;
  children: React.ReactNode;
}

export interface CardContentProps {
  className?: string;
  children: React.ReactNode;
}

export interface CardFooterProps {
  className?: string;
  children: React.ReactNode;
}

const Card = ({ className, children }: CardProps) => {
  return (
    <div
      className={cn(
        'bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden',
        className
      )}
    >
      {children}
    </div>
  );
};

const CardHeader = ({ className, children }: CardHeaderProps) => {
  return (
    <div
      className={cn('px-6 py-4 border-b border-gray-200', className)}
    >
      {children}
    </div>
  );
};

const CardTitle = ({ className, children }: CardTitleProps) => {
  return (
    <h3
      className={cn('text-xl font-semibold text-gray-900', className)}
    >
      {children}
    </h3>
  );
};

const CardDescription = ({ className, children }: CardDescriptionProps) => {
  return (
    <p
      className={cn('mt-1 text-sm text-gray-500', className)}
    >
      {children}
    </p>
  );
};

const CardContent = ({ className, children }: CardContentProps) => {
  return (
    <div
      className={cn('px-6 py-4', className)}
    >
      {children}
    </div>
  );
};

const CardFooter = ({ className, children }: CardFooterProps) => {
  return (
    <div
      className={cn('px-6 py-4 bg-gray-50 border-t border-gray-200', className)}
    >
      {children}
    </div>
  );
};

Card.Header = CardHeader;
Card.Title = CardTitle;
Card.Description = CardDescription;
Card.Content = CardContent;
Card.Footer = CardFooter;

export default Card; 
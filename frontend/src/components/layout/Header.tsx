import React from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';

export interface HeaderProps {
  className?: string;
}

const Header = ({ className }: HeaderProps) => {
  return (
    <header className={cn('bg-blue-600 text-white shadow-md', className)}>
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <div>
          <Link href="/" className="flex items-center">
            <span className="text-2xl font-bold">Customer Support Chatbot</span>
          </Link>
          <p className="text-sm text-blue-100">Ask questions about insurance plans</p>
        </div>
        
        <nav className="hidden md:flex space-x-6">
          <Link 
            href="/" 
            className="text-white hover:text-blue-200 transition-colors"
          >
            Home
          </Link>
          <Link 
            href="/documents" 
            className="text-white hover:text-blue-200 transition-colors"
          >
            Documents
          </Link>
          <Link 
            href="/about" 
            className="text-white hover:text-blue-200 transition-colors"
          >
            About
          </Link>
        </nav>
      </div>
    </header>
  );
};

export default Header; 
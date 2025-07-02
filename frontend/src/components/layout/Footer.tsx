import React from 'react';
import { cn } from '@/lib/utils';

export interface FooterProps {
  className?: string;
}

const Footer = ({ className }: FooterProps) => {
  return (
    <footer className={cn('bg-gray-100 py-6', className)}>
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <p className="text-gray-600 text-sm">
              Customer Support Chatbot - Powered by Hemant
            </p>
          </div>
          
          <div className="flex space-x-4">
            <a 
              href="#" 
              className="text-gray-600 hover:text-blue-600 text-sm"
            >
              Terms of Service
            </a>
            <a 
              href="#" 
              className="text-gray-600 hover:text-blue-600 text-sm"
            >
              Privacy Policy
            </a>
            <a 
              href="#" 
              className="text-gray-600 hover:text-blue-600 text-sm"
            >
              Contact
            </a>
          </div>
        </div>
        
        <div className="mt-4 text-center text-xs text-gray-500">
          &copy; {new Date().getFullYear()} Customer Support Chatbot. All rights reserved.
        </div>
      </div>
    </footer>
  );
};

export default Footer; 
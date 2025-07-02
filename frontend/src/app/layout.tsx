import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import dynamic from 'next/dynamic';
import ChatIntro from '@/components/chat/ChatIntro';

const inter = Inter({ subsets: ['latin'] });

// Import HydrationProvider with dynamic import to avoid SSR
const HydrationProvider = dynamic(
  () => import('@/components/HydrationProvider'),
  { ssr: false }
);

export const metadata: Metadata = {
  title: 'Customer Support Chatbot',
  description: 'A chatbot that answers questions about insurance plans using RAG technology',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} flex flex-col h-full bg-angel-gray-50`}>
        <header className="bg-violet-700 text-white p-4 shadow-lg flex-shrink-0">
          <div className="container mx-auto flex justify-between items-center">
            <h1 className="text-3xl font-extrabold tracking-tight">Customer Support Chatbot</h1>
            <p className="text-sm opacity-90 hidden sm:block">Your intelligent assistant for insurance queries</p>
          </div>
        </header>
        <main className="flex-grow w-full flex flex-row h-[calc(100vh-8rem)]">
          {/* Left: ChatIntro */}
          <div className="hidden lg:block w-[400px] min-w-[320px] max-w-[480px] h-full">
            <ChatIntro />
          </div>
          {/* Right: Page content */}
          <div className="flex-1 h-full">
            <HydrationProvider>
              {children}
            </HydrationProvider>
          </div>
        </main>
        <footer className="bg-angel-gray-800 p-4 text-center text-angel-gray-300 text-sm shadow-inner flex-shrink-0">
          <div className="container mx-auto">
            <p>&copy; {new Date().getFullYear()} Customer Support Chatbot. All rights reserved.</p>
            <p className="mt-1">Powered by Hemant</p>
          </div>
        </footer>
      </body>
    </html>
  );
} 
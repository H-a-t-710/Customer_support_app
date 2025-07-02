import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import dynamic from 'next/dynamic';

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
        <div className="flex flex-col h-full w-full">
          <header className="bg-violet-700 text-white p-4 shadow-lg flex-shrink-0">
            <div className="container mx-auto flex justify-between items-center">
              <h1 className="text-xl font-bold tracking-tight">Customer Support . ChatBot</h1>
              <p className="text-sm opacity-90 hidden sm:block">Your intelligent assistant for insurance queries</p>
            </div>
          </header>
          <main className="flex-grow w-full h-full">
            <HydrationProvider>
              {children}
            </HydrationProvider>
          </main>
          <footer className="bg-angel-gray-800 p-4 text-center text-angel-gray-300 text-sm shadow-inner flex-shrink-0">
            <div className="container mx-auto">
              <p>&copy; {new Date().getFullYear()} Customer Support Chatbot. All rights reserved.</p>
              <p className="mt-1">Powered by Hemant</p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
} 
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
  title: 'Insurance RAG Chatbot',
  description: 'A chatbot that answers questions about insurance plans using RAG technology',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="flex flex-col min-h-screen">
          <header className="bg-blue-600 text-white p-4 shadow-md">
            <div className="container mx-auto">
              <h1 className="text-2xl font-bold">Insurance RAG Chatbot</h1>
              <p className="text-sm">Ask questions about insurance plans</p>
            </div>
          </header>
          <main className="flex-grow container mx-auto p-4">
            <HydrationProvider>
              {children}
            </HydrationProvider>
          </main>
          <footer className="bg-gray-100 p-4 text-center text-gray-600 text-sm">
            <p>Insurance RAG Chatbot - Powered by Gemini</p>
          </footer>
        </div>
      </body>
    </html>
  );
} 
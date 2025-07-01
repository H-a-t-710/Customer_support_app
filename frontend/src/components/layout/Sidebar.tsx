import React from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import useChatStore from '@/store/chatStore';
import { formatRelativeTime } from '@/lib/utils';
import { MessageSquare, Plus, Trash2 } from 'lucide-react';

export interface SidebarProps {
  className?: string;
}

const Sidebar = ({ className }: SidebarProps) => {
  const { 
    sessions, 
    currentSessionId, 
    createSession, 
    switchSession, 
    deleteSession 
  } = useChatStore();

  const sessionsList = Object.values(sessions).sort(
    (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
  );

  return (
    <aside 
      className={cn(
        'w-64 bg-gray-50 border-r border-gray-200 flex flex-col h-full',
        className
      )}
    >
      <div className="p-4">
        <button
          onClick={() => createSession()}
          className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md transition-colors"
        >
          <Plus size={18} />
          <span>New Chat</span>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-2">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider px-2 mb-2">
          Recent Conversations
        </h3>
        
        {sessionsList.length === 0 ? (
          <div className="text-sm text-gray-500 px-2">
            No conversations yet
          </div>
        ) : (
          <ul className="space-y-1">
            {sessionsList.map((session) => (
              <li key={session.id}>
                <div 
                  className={cn(
                    'flex items-center justify-between px-3 py-2 rounded-md text-sm cursor-pointer',
                    currentSessionId === session.id 
                      ? 'bg-blue-100 text-blue-800' 
                      : 'hover:bg-gray-100 text-gray-700'
                  )}
                >
                  <div 
                    className="flex items-center gap-2 flex-1 overflow-hidden"
                    onClick={() => switchSession(session.id)}
                  >
                    <MessageSquare size={16} />
                    <span className="truncate">{session.name}</span>
                  </div>
                  
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteSession(session.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 hover:text-red-600 p-1"
                    title="Delete conversation"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
                
                <div className="text-xs text-gray-500 ml-9 mt-1 mb-2">
                  {formatRelativeTime(session.updatedAt)}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
      
      <div className="p-4 border-t border-gray-200">
        <nav className="space-y-1">
          <Link 
            href="/documents" 
            className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
          >
            Documents
          </Link>
          <Link 
            href="/about" 
            className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
          >
            About
          </Link>
        </nav>
      </div>
    </aside>
  );
};

export default Sidebar; 
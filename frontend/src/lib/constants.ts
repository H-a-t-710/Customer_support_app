/**
 * API Constants
 */
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

/**
 * Chat Constants
 */
export const MAX_MESSAGE_LENGTH = 4000;
export const DEFAULT_SYSTEM_MESSAGE = 
  "You are an AI assistant that helps with insurance questions. " +
  "Answer questions based only on the provided insurance documents. " +
  "If you don't know the answer, say 'I don't know' or 'I don't have that information.'";

/**
 * Document Constants
 */
export const ALLOWED_FILE_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain',
  'text/csv',
];

export const FILE_TYPE_MAP: Record<string, string> = {
  'application/pdf': 'PDF',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'DOCX',
  'text/plain': 'TXT',
  'text/csv': 'CSV',
};

export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

/**
 * UI Constants
 */
export const THEME_COLORS = {
  primary: '#2563eb', // blue-600
  secondary: '#6b7280', // gray-500
  success: '#10b981', // emerald-500
  danger: '#ef4444', // red-500
  warning: '#f59e0b', // amber-500
  info: '#3b82f6', // blue-500
};

export const ANIMATION_DURATION = 300; // ms 
/**
 * Types related to document functionality
 */

export enum DocumentStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export enum DocumentType {
  PDF = 'pdf',
  DOCX = 'docx',
  TXT = 'txt',
  CSV = 'csv',
}

export interface Document {
  id: string;
  filename: string;
  type: DocumentType;
  status: DocumentStatus;
  size: number; // in bytes
  pages?: number;
  createdAt: string;
  updatedAt: string;
  error?: string;
  metadata?: Record<string, any>;
}

export interface DocumentUploadResponse {
  document: Document;
  message: string;
}

export interface DocumentStatusResponse {
  document: Document;
}

export interface DocumentsListResponse {
  documents: Document[];
}

export interface DocumentDeleteResponse {
  success: boolean;
  message: string;
} 
import { Document } from '@/types/document';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

/**
 * Fetch all documents in the system
 */
export async function fetchDocuments(): Promise<Document[]> {
  try {
    const response = await fetch(`${API_URL}/documents`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `Error ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching documents:', error);
    throw error;
  }
}

/**
 * Upload a new document to the system
 */
export async function uploadDocument(file: File): Promise<Document> {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_URL}/documents/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `Error ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error uploading document:', error);
    throw error;
  }
}

/**
 * Delete a document from the system
 */
export async function deleteDocument(documentId: string): Promise<void> {
  try {
    const response = await fetch(`${API_URL}/documents/${documentId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `Error ${response.status}: ${response.statusText}`);
    }
  } catch (error) {
    console.error(`Error deleting document ${documentId}:`, error);
    throw error;
  }
}

/**
 * Get document processing status
 */
export async function getDocumentStatus(documentId: string): Promise<Document> {
  try {
    const response = await fetch(`${API_URL}/documents/${documentId}/status`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `Error ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`Error getting document status ${documentId}:`, error);
    throw error;
  }
} 
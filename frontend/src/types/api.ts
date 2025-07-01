/**
 * Types related to API responses and requests
 */

export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

export interface ApiError {
  status: number;
  message: string;
  details?: Record<string, any>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface ApiConfig {
  baseUrl: string;
  headers?: Record<string, string>;
  timeout?: number;
} 
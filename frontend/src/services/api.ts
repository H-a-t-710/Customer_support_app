import { ApiConfig, ApiError } from '@/types/api';
import { API_URL } from '@/lib/constants';

const defaultConfig: ApiConfig = {
  baseUrl: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
};

/**
 * Create a configured API client
 */
export function createApiClient(config: Partial<ApiConfig> = {}) {
  const apiConfig: ApiConfig = {
    ...defaultConfig,
    ...config,
    headers: {
      ...defaultConfig.headers,
      ...config.headers,
    },
  };

  /**
   * Make a GET request
   */
  async function get<T>(path: string, params?: Record<string, string>) {
    const url = new URL(`${apiConfig.baseUrl}${path}`);
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, value);
      });
    }
    
    try {
      const response = await fetch(url.toString(), {
        method: 'GET',
        headers: apiConfig.headers,
      });
      
      return handleResponse<T>(response);
    } catch (error) {
      return handleError(error);
    }
  }

  /**
   * Make a POST request
   */
  async function post<T>(path: string, data?: any) {
    try {
      const response = await fetch(`${apiConfig.baseUrl}${path}`, {
        method: 'POST',
        headers: apiConfig.headers,
        body: data ? JSON.stringify(data) : undefined,
      });
      
      return handleResponse<T>(response);
    } catch (error) {
      return handleError(error);
    }
  }

  /**
   * Make a PUT request
   */
  async function put<T>(path: string, data?: any) {
    try {
      const response = await fetch(`${apiConfig.baseUrl}${path}`, {
        method: 'PUT',
        headers: apiConfig.headers,
        body: data ? JSON.stringify(data) : undefined,
      });
      
      return handleResponse<T>(response);
    } catch (error) {
      return handleError(error);
    }
  }

  /**
   * Make a DELETE request
   */
  async function del<T>(path: string) {
    try {
      const response = await fetch(`${apiConfig.baseUrl}${path}`, {
        method: 'DELETE',
        headers: apiConfig.headers,
      });
      
      return handleResponse<T>(response);
    } catch (error) {
      return handleError(error);
    }
  }

  /**
   * Handle API response
   */
  async function handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw {
        status: response.status,
        message: errorData.message || response.statusText,
        details: errorData,
      };
    }
    
    // Handle no content responses
    if (response.status === 204) {
      return {} as T;
    }
    
    return await response.json();
  }

  /**
   * Handle API error
   */
  function handleError(error: any): never {
    const apiError: ApiError = {
      status: error.status || 500,
      message: error.message || 'An unexpected error occurred',
      details: error.details,
    };
    
    console.error('API Error:', apiError);
    throw apiError;
  }

  return {
    get,
    post,
    put,
    delete: del,
  };
}

// Create a default API client
export const api = createApiClient(); 
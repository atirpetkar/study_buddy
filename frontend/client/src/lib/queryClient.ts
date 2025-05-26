import { QueryClient, QueryFunction } from "@tanstack/react-query";
import { API_BASE_URL } from "./config";

async function throwIfResNotOk(res: Response) {
  if (!res.ok) {
    // Handle 401 Unauthorized to redirect to login
    if (res.status === 401) {
      // Clear token as it might be expired
      localStorage.removeItem('authToken');
      // Specific error for unauthorized
      throw new Error('Authentication required. Please log in again.');
    }
    
    let errorText;
    try {
      // Try to parse as JSON first
      const errorData = await res.json();
      errorText = errorData.detail || errorData.message || JSON.stringify(errorData);
    } catch (e) {
      // Fallback to text if not JSON
      errorText = await res.text() || res.statusText;
    }
    
    throw new Error(`${res.status}: ${errorText}`);
  }
}

export async function apiRequest(
  method: string,
  endpoint: string,
  data?: unknown | undefined,
): Promise<Response> {
  try {
    const url = `${API_BASE_URL}${endpoint}`;
    
    // Add auth token from localStorage if available
    const headers: HeadersInit = {};
    if (data && !(data instanceof FormData)) {
      headers["Content-Type"] = "application/json";
    }
    
    // Add accept header for JSON responses
    headers["Accept"] = "application/json";
    
    const authToken = localStorage.getItem('authToken');
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    const options: RequestInit = {
      method,
      headers,
      // For cross-domain requests, use 'omit' instead of 'include'
      credentials: "omit",
      // Explicitly set CORS mode
      mode: "cors",
    };
    
    // Only add body if data exists
    if (data) {
      if (data instanceof FormData) {
        options.body = data;
      } else {
        options.body = JSON.stringify(data);
      }
    }
    
    console.log(`Making ${method} request to ${url} with options:`, {
      headers: options.headers,
      body: options.body ? '[data present]' : undefined
    });
    
    const res = await fetch(url, options);
    
    // Log response details
    console.log(`Response from ${method} ${url}:`, {
      status: res.status,
      statusText: res.statusText,
      contentType: res.headers.get('content-type'),
      cors: res.headers.get('access-control-allow-origin')
    });
    
    await throwIfResNotOk(res);
    return res;
  } catch (error) {
    console.error(`API ${method} request to ${endpoint} failed:`, error);
    throw error;
  }
}

type UnauthorizedBehavior = "returnNull" | "throw";
export const getQueryFn: <T>(options: {
  on401: UnauthorizedBehavior;
}) => QueryFunction<T> =
  ({ on401: unauthorizedBehavior }) =>
  async ({ queryKey }) => {
    try {
      // Add auth token from localStorage if available
      const headers: HeadersInit = {
        'Accept': 'application/json'
      };
      
      const authToken = localStorage.getItem('authToken');
      if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
      }
      
      // Prepend API_BASE_URL to the query path
      const queryPath = queryKey[0] as string;
      const url = queryPath.startsWith('http') ? queryPath : `${API_BASE_URL}${queryPath}`;
      
      console.log(`Query function making request to: ${url}`);
      
      const res = await fetch(url, {
        // For cross-domain requests, use 'omit' instead of 'include'
        credentials: "omit",
        // Explicitly set CORS mode
        mode: "cors",
        headers
      });

      console.log(`Query response from ${url}:`, {
        status: res.status,
        statusText: res.statusText,
        contentType: res.headers.get('content-type')
      });
  
      if (unauthorizedBehavior === "returnNull" && res.status === 401) {
        return null;
      }
  
      await throwIfResNotOk(res);
      return await res.json();
    } catch (error) {
      console.error(`Query function error for ${JSON.stringify(queryKey)}:`, error);
      throw error;
    }
  };

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      queryFn: getQueryFn({ on401: "throw" }),
      refetchInterval: false,
      refetchOnWindowFocus: false,
      staleTime: Infinity,
      retry: false,
    },
    mutations: {
      retry: false,
    },
  },
});

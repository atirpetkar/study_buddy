import { API_BASE_URL } from '../config';

/**
 * Service for debugging and sending diagnostic information to the server
 */
export const debugService = {
  /**
   * Log client-side error to help with backend debugging
   */
  logError: async (error: any, context: string, additionalData?: any) => {
    // Don't crash if this fails - it's just for debugging
    try {
      const errorData = {
        message: error instanceof Error ? error.message : String(error),
        stack: error instanceof Error ? error.stack : undefined,
        context,
        timestamp: new Date().toISOString(),
        additionalData,
        userAgent: navigator.userAgent,
        url: window.location.href
      };
      
      console.error('Debug error log:', errorData);
      
      // Only send to server if we have a real API URL
      if (!API_BASE_URL.startsWith('/')) {
        const response = await fetch(`${API_BASE_URL}/debug/log`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(errorData),
          // Don't include credentials for debug endpoints
          credentials: 'omit',
        });
        
        console.log('Debug log response:', response.status);
      }
    } catch (e) {
      // Don't do anything if debug logging fails
      console.warn('Debug logging failed:', e);
    }
  },
  
  /**
   * Check if a GET API endpoint is accessible and functioning
   */
  pingEndpoint: async (endpoint: string): Promise<{
    success: boolean;
    status?: number;
    message?: string;
    responseTime: number;
  }> => {
    const start = Date.now();
    try {
      const url = `${API_BASE_URL}${endpoint}`;
      const response = await fetch(url, {
        method: 'GET',
        credentials: 'omit',
      });
      
      const end = Date.now();
      const responseTime = end - start;
      
      return {
        success: response.ok,
        status: response.status,
        message: response.ok ? 'Endpoint is accessible' : await response.text(),
        responseTime
      };
    } catch (error) {
      const end = Date.now();
      const responseTime = end - start;
      
      return {
        success: false,
        message: error instanceof Error ? error.message : String(error),
        responseTime
      };
    }
  },
  
  /**
   * Test a POST endpoint with sample data
   */
  testPostEndpoint: async (endpoint: string, data: any): Promise<{
    success: boolean;
    status?: number;
    message?: string;
    responseTime: number;
    response?: any;
  }> => {
    const start = Date.now();
    try {
      const url = `${API_BASE_URL}${endpoint}`;
      console.log(`Testing POST endpoint: ${url}`, data);
      
      // For the chat endpoint, ensure we use exactly the correct schema format
      if (endpoint === '/chat/chat') {
        // Make sure data has the exact expected fields for ChatRequest
        if (!data.user_id || !data.message || !data.mode) {
          console.warn('Correcting data format for chat endpoint...');
          // If it doesn't, try to map to the correct format
          data = {
            user_id: data.user_id || data.userId || 'default-user',
            message: data.message || data.text || 'Default test message',
            mode: data.mode || 'chat'
          };
        }
      }
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(data),
        credentials: 'omit',
        mode: 'cors'
      });
      
      const end = Date.now();
      const responseTime = end - start;
      
      let responseData;
      let message;
      
      try {
        responseData = await response.json();
        message = response.ok 
          ? 'Endpoint responded successfully' 
          : responseData.detail || JSON.stringify(responseData);
      } catch (e) {
        const text = await response.text();
        message = text || response.statusText;
        responseData = { text };
      }
      
      return {
        success: response.ok,
        status: response.status,
        message,
        responseTime,
        response: responseData
      };
    } catch (error) {
      const end = Date.now();
      const responseTime = end - start;
      
      return {
        success: false,
        message: error instanceof Error ? error.message : String(error),
        responseTime
      };
    }
  }
}; 
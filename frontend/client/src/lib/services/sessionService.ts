import { apiRequest } from '../queryClient';
import { API_BASE_URL } from '../config';

// Study Sessions
export const createQuickSession = async (data: { user_id: string; topic: string; duration_minutes: number }) => {
  try {
    console.log("Creating session with data:", data);
    console.log("API request URL:", `${API_BASE_URL}/session/quick`);
    
    const response = await apiRequest('POST', '/session/quick', data);
    console.log("API response status:", response.status);
    
    const responseData = await response.json();
    console.log("Session creation full response:", responseData);
    
    if (!response.ok) {
      console.error("Error response from server:", responseData);
      throw new Error(responseData.detail || 'Failed to create session');
    }
    
    // Verify the response has the expected format
    if (!responseData.session_id) {
      console.error("Missing session_id in response:", responseData);
      throw new Error('Invalid response format: missing session_id');
    }
    
    return responseData;
  } catch (error) {
    console.error("Error creating session:", error);
    throw error;
  }
};

export const executeActivity = async (data: { session_id: string; activity_index: number }) => {
  const response = await apiRequest('POST', '/session/execute', data);
  return response.json();
};

export const getUserSessions = async (user_id: string) => {
  const response = await apiRequest('GET', `/session/user/${user_id}`);
  return response.json();
};

export const sessionService = {
  createQuickSession,
  executeActivity,
  getUserSessions,
}; 
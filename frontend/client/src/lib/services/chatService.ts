import { apiRequest } from '../queryClient';
import { logApiError, formatErrorMessage } from '../errorHandler';
import { API_BASE_URL, DEFAULT_USER_ID } from '../config';

// Correct endpoint based on the FastAPI router in app/api/chat.py
// The router is prefixed with '/chat' and the endpoint is '/chat', so full path is '/chat/chat'
const CHAT_ENDPOINT = '/chat/chat';

// Format the payload in different ways that the backend might expect
function formatPayloads(data: {
  user_id: string;
  message: string;
  mode: 'chat' | 'tutor' | 'quiz' | 'flashcard';
}) {
  return [
    // Original format
    data,
    
    // Alternative formats
    {
      userId: data.user_id,
      message: data.message,
      mode: data.mode
    },
    {
      user: data.user_id,
      query: data.message,
      mode: data.mode
    },
    {
      message: data.message,
      mode: data.mode
    }
  ];
}

// Chat & Tutoring
export const sendChatMessage = async (data: {
  user_id: string;
  message: string;
  mode: 'chat' | 'tutor' | 'quiz' | 'flashcard';
}) => {
  try {
    const endpoint = `${API_BASE_URL}${CHAT_ENDPOINT}`;
    console.log('Sending chat message to backend with exact schema format:', data);
    console.log('Chat endpoint URL:', endpoint);
    
    // Send request with exact structure matching ChatRequest schema
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        user_id: data.user_id,
        message: data.message,
        mode: data.mode
      }),
      // For local development with different ports
      mode: 'cors',
      // For local development without cookies
      credentials: 'omit',
    });
    
    console.log('Chat response status:', response.status);
    console.log('Chat response headers:', {
      contentType: response.headers.get('content-type'),
      cors: response.headers.get('access-control-allow-origin')
    });
    
    if (!response.ok) {
      let errorText;
      try {
        const errorData = await response.json();
        errorText = errorData.detail || JSON.stringify(errorData);
      } catch (e) {
        errorText = await response.text() || response.statusText;
      }
      console.error('Chat error response:', errorText);
      throw new Error(`Error ${response.status}: ${errorText}`);
    }
    
    const responseData = await response.json();
    console.log('Chat response data:', responseData);
    return responseData;
  } catch (error) {
    console.error('Chat service error:', error);
    logApiError(error, 'sendChatMessage');
    throw new Error(formatErrorMessage(error, 'Failed to send message'));
  }
};

// Try a simpler payload format that might be more compatible with the backend
export const sendSimpleChatMessage = async (message: string) => {
  try {
    console.log('Sending simple chat message with user_id:', DEFAULT_USER_ID);
    
    const response = await fetch(`${API_BASE_URL}${CHAT_ENDPOINT}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ 
        user_id: DEFAULT_USER_ID, 
        message,
        mode: 'chat' // Required by ChatRequest schema
      }),
      credentials: 'omit',
      mode: 'cors',
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Error ${response.status}: ${errorText}`);
    }
    
    return response.json();
  } catch (error) {
    console.error('Simple chat error:', error);
    throw error;
  }
};

export const chatService = {
  sendMessage: sendChatMessage,
  sendSimpleMessage: sendSimpleChatMessage
}; 
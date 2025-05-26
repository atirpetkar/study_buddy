import { apiRequest } from './queryClient';
import { API_BASE_URL } from './config';

// Document Management
export const uploadDocuments = async (files: FileList) => {
  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    formData.append('files', files[i]);
  }
  
  const response = await fetch(`${API_BASE_URL}/vectorstore/upload`, {
    method: 'POST',
    body: formData,
    credentials: 'include',
  });
  
  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || 'Failed to upload documents');
  }
  
  return response.json();
};

export const getDocuments = async () => {
  const response = await apiRequest('GET', '/vectorstore/documents');
  return response.json();
};

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

// Learning Content
export const generateQuiz = async (data: { 
  user_id: string;
  topic: string;
  num_questions: number;
  difficulty: string;
  save_quiz?: boolean;
}) => {
  const response = await apiRequest('POST', '/quiz/generate', data);
  return response.json();
};

export const getUserQuizzes = async (user_id: string) => {
  const response = await apiRequest('GET', `/quiz/user/${user_id}`);
  return response.json();
};

export const generateFlashcards = async (data: {
  user_id: string;
  topic: string;
  num_cards: number;
  save_flashcards?: boolean;
}) => {
  const response = await apiRequest('POST', '/flashcard/generate', data);
  return response.json();
};

// Chat & Tutoring
export const sendChatMessage = async (data: {
  user_id: string;
  message: string;
  mode: 'chat' | 'tutor' | 'quiz' | 'flashcard';
}) => {
  const response = await apiRequest('POST', '/chat/chat', data);
  return response.json();
};

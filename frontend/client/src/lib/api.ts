import { apiRequest } from './queryClient';

// Document Management
export const uploadDocuments = async (files: FileList) => {
  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    formData.append('files', files[i]);
  }
  
  const response = await fetch('/api/vectorstore/upload', {
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
  const response = await fetch('/api/vectorstore/documents', {
    credentials: 'include',
  });
  
  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || 'Failed to get documents');
  }
  
  return response.json();
};

// Study Sessions
export const createQuickSession = async (data: { user_id: string; topic: string; duration_minutes: number }) => {
  const response = await apiRequest('POST', '/api/session/quick', data);
  return response.json();
};

export const executeActivity = async (data: { session_id: string; activity_index: number }) => {
  const response = await apiRequest('POST', '/api/session/execute', data);
  return response.json();
};

export const getUserSessions = async (user_id: string) => {
  const response = await fetch(`/api/session/user/${user_id}`, {
    credentials: 'include',
  });
  
  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || 'Failed to get user sessions');
  }
  
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
  const response = await apiRequest('POST', '/api/quiz/generate', data);
  return response.json();
};

export const getUserQuizzes = async (user_id: string) => {
  const response = await fetch(`/api/quiz/user/${user_id}`, {
    credentials: 'include',
  });
  
  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || 'Failed to get user quizzes');
  }
  
  return response.json();
};

export const generateFlashcards = async (data: {
  user_id: string;
  topic: string;
  num_cards: number;
  save_flashcards?: boolean;
}) => {
  const response = await apiRequest('POST', '/api/flashcard/generate', data);
  return response.json();
};

// Chat & Tutoring
export const sendChatMessage = async (data: {
  user_id: string;
  message: string;
  mode: 'chat' | 'tutor' | 'quiz' | 'flashcard';
}) => {
  const response = await apiRequest('POST', '/api/chat/chat', data);
  return response.json();
};

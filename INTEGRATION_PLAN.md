# Study Buddy - Frontend/Backend Integration Plan

This document outlines the step-by-step plan for integrating the React frontend with the FastAPI backend for the Study Buddy AI Agent Hackathon project.

## Phase 1: Basic Setup and Configuration (COMPLETED)

**Step 1: Configure Backend for Frontend Access**
```python
# The CORS configuration is already in place in main.py
# Properly configured for development with allow_origins=['*']
```

**Step 2: Create API Configuration in Frontend**
```typescript
// Created config file at frontend/client/src/lib/config.ts
export const API_BASE_URL = 'http://localhost:8000'; // Adjust if your FastAPI runs on a different port
```

**Step 3: Update Existing API Client Adapter**
```typescript
// Updated the existing frontend/client/src/lib/queryClient.ts instead of creating a new apiAdapter
import { QueryClient, QueryFunction } from "@tanstack/react-query";
import { API_BASE_URL } from "./config";

// ...existing code...

export async function apiRequest(
  method: string,
  endpoint: string,
  data?: unknown | undefined,
): Promise<Response> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const res = await fetch(url, {
    method,
    headers: data ? { "Content-Type": "application/json" } : {},
    body: data ? JSON.stringify(data) : undefined,
    credentials: "include",
  });

  await throwIfResNotOk(res);
  return res;
}

// ...existing code...
```

**Step 4: Update API Endpoints**
```typescript
// Updated frontend/client/src/lib/api.ts to use the API_BASE_URL
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
  
  // ...existing code...
};

// ...other API functions updated...
```

## Phase 2: User Authentication Integration (Day 2)

**Step 5: Connect User Authentication**
```typescript
// Update or create authentication services using the existing pattern

// If auth features don't exist yet:
// Create frontend/client/src/lib/services/authService.ts
import { apiRequest } from '../queryClient';
import { API_BASE_URL } from '../config';

export const authService = {
  login: async (username: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await fetch(`${API_BASE_URL}/users/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
      credentials: 'include',
    });
    
    if (!response.ok) {
      throw new Error('Authentication failed');
    }
    
    const data = await response.json();
    // Store token in localStorage for subsequent requests
    localStorage.setItem('authToken', data.access_token);
    return data;
  },
  
  getCurrentUser: async () => {
    const response = await apiRequest('GET', '/users/me');
    return response.json();
  },
  
  logout: async () => {
    localStorage.removeItem('authToken');
  }
};
```

**Step 6: Create Auth Context for State Management**
```typescript
// Create frontend/client/src/context/AuthContext.tsx if it doesn't exist yet
import React, { createContext, useState, useEffect, useContext } from 'react';
import { authService } from '../lib/services/authService';

const AuthContext = createContext<{
  user: any | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
  isLoading: boolean;
}>({
  user: null,
  login: async () => {},
  logout: async () => {},
  isAuthenticated: false,
  isLoading: true
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    // Check if user is already logged in
    const checkAuth = async () => {
      try {
        if (localStorage.getItem('authToken')) {
          const userData = await authService.getCurrentUser();
          setUser(userData);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        localStorage.removeItem('authToken');
      } finally {
        setIsLoading(false);
      }
    };
    
    checkAuth();
  }, []);
  
  const login = async (username: string, password: string) => {
    const result = await authService.login(username, password);
    setUser(result.user);
  };
  
  const logout = async () => {
    await authService.logout();
    setUser(null);
  };
  
  return (
    <AuthContext.Provider value={{
      user,
      login,
      logout,
      isAuthenticated: !!user,
      isLoading
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
```

## Phase 3: Core API Service Integration (COMPLETED)

**Step 7: Organize Existing API Functions into Services**
```typescript
// Refactor existing API functions into service modules, using the existing pattern

// Create frontend/client/src/lib/services/documentService.ts
import { apiRequest } from '../queryClient';
import { API_BASE_URL } from '../config';
import { uploadDocuments, getDocuments } from '../api';

// Export the functions directly or re-implement them in a service object
export const documentService = {
  uploadDocuments,
  getDocuments,
};

// Create frontend/client/src/lib/services/chatService.ts
import { apiRequest } from '../queryClient';
import { sendChatMessage } from '../api';

export const chatService = {
  sendMessage: sendChatMessage,
};

// Create frontend/client/src/lib/services/sessionService.ts
import { apiRequest } from '../queryClient';
import { createQuickSession, executeActivity, getUserSessions } from '../api';

export const sessionService = {
  createQuickSession,
  executeActivity,
  getUserSessions,
};
```

## Phase 4: React Component Integration (Day 4-5)

**Step 8: Update App.tsx with Auth Provider**
```typescript
// Update frontend/client/src/App.tsx to include AuthProvider
import { AuthProvider } from './context/AuthContext';

function App() {
  return (
    <AuthProvider>
      <QueryClientProvider client={queryClient}>
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </QueryClientProvider>
    </AuthProvider>
  );
}
```

**Step 9: Connect Document Management Components**
```typescript
// Update frontend/client/src/pages/DocumentsPage.tsx to use services
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentService } from '@/lib/services/documentService';

export default function DocumentsPage() {
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");
  
  const { data, isLoading, error } = useQuery({
    queryKey: ['documents'],
    queryFn: documentService.getDocuments
  });
  
  const uploadMutation = useMutation({
    mutationFn: documentService.uploadDocuments,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    }
  });
  
  const handleFileUpload = async (files: FileList) => {
    try {
      await uploadMutation.mutateAsync(files);
    } catch (error) {
      console.error('Upload error:', error);
    }
  };
  
  // Render document page UI
}
```

**Step 10: Connect Chat Interface**
```typescript
// Update frontend/client/src/components/chat/ChatInterface.tsx
import { useState } from 'react';
import { chatService } from '@/lib/services/chatService';
import { useAuth } from '@/context/AuthContext';

export default function ChatInterface() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<any[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  
  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;
    
    const userMessage = {
      content: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };
    
    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);
    
    try {
      const response = await chatService.sendMessage({
        user_id: user?.id || 'guest',
        message: inputMessage,
        mode: 'chat'
      });
      
      const botMessage = {
        content: response.response,
        sender: 'assistant',
        timestamp: new Date(),
        context: response.context_used
      };
      
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages((prev) => [...prev, {
        content: 'Sorry, there was an error processing your request.',
        sender: 'system',
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Render chat interface UI
}
```

## Phase 5: Study Session Integration (Day 6)

**Step 11: Connect Study Session Components**
```typescript
// Update frontend/client/src/pages/CreateSessionPage.tsx
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { sessionService } from '@/lib/services/sessionService';
import { useAuth } from '@/context/AuthContext';
import { useLocation } from 'wouter';

const sessionFormSchema = z.object({
  topic: z.string().min(3).max(100),
  duration_minutes: z.number().min(5).max(120)
});

export default function CreateSessionPage() {
  const { user } = useAuth();
  const [_, setLocation] = useLocation();
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const form = useForm<z.infer<typeof sessionFormSchema>>({
    resolver: zodResolver(sessionFormSchema),
    defaultValues: {
      topic: '',
      duration_minutes: 30
    }
  });
  
  const onSubmit = async (data: z.infer<typeof sessionFormSchema>) => {
    setIsSubmitting(true);
    try {
      const result = await sessionService.createQuickSession({
        user_id: user?.id || 'guest',
        ...data
      });
      
      setLocation(`/session/${result.session_id}`);
    } catch (error) {
      console.error('Session creation error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  // Render session creation form UI
}
```

**Step 12: Connect Session List Page**
```typescript
// Update frontend/client/src/pages/SessionsPage.tsx
import { useQuery } from '@tanstack/react-query';
import { sessionService } from '@/lib/services/sessionService';
import { useAuth } from '@/context/AuthContext';

export default function SessionsPage() {
  const { user } = useAuth();
  const [_, setLocation] = useLocation();
  
  const { data: sessions, isLoading, error } = useQuery({
    queryKey: ['sessions', user?.id],
    queryFn: () => sessionService.getUserSessions(user?.id || 'guest'),
    enabled: !!user
  });
  
  const handleCreateSession = () => {
    setLocation('/create-session');
  };
  
  const handleSessionClick = (sessionId: string) => {
    setLocation(`/session/${sessionId}`);
  };
  
  // Render sessions list UI
}
```

## Phase 6: Learning Content Integration (Day 7)

**Step 13: Connect Quiz Components**
```typescript
// Create frontend/client/src/lib/services/quizService.ts
import { apiRequest } from '../queryClient';
import { generateQuiz, getUserQuizzes } from '../api';

export const quizService = {
  generateQuiz,
  getUserQuizzes
};

// Update frontend/client/src/pages/QuizzesPage.tsx
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { quizService } from '@/lib/services/quizService';
import { useAuth } from '@/context/AuthContext';

export default function QuizzesPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  
  const { data: quizzes, isLoading } = useQuery({
    queryKey: ['quizzes', user?.id],
    queryFn: () => quizService.getUserQuizzes(user?.id || 'guest'),
    enabled: !!user
  });
  
  const generateQuizMutation = useMutation({
    mutationFn: quizService.generateQuiz,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['quizzes', user?.id] });
    }
  });
  
  const handleCreateQuiz = async (formData) => {
    setIsGenerating(true);
    try {
      await generateQuizMutation.mutateAsync({
        user_id: user?.id || 'guest',
        topic: formData.topic,
        num_questions: formData.numQuestions,
        difficulty: formData.difficulty
      });
    } catch (error) {
      console.error('Quiz generation error:', error);
    } finally {
      setIsGenerating(false);
    }
  };
  
  // Render quizzes list UI
}
```

**Step 14: Connect Flashcard Components**
```typescript
// Create frontend/client/src/lib/services/flashcardService.ts
import { apiRequest } from '../queryClient';
import { generateFlashcards } from '../api';

export const flashcardService = {
  generateFlashcards,
  getUserFlashcards: async (user_id?: string) => {
    const endpoint = user_id ? `/flashcards?user_id=${user_id}` : '/flashcards';
    const response = await apiRequest('GET', endpoint);
    return response.json();
  }
};

// Update frontend/client/src/pages/FlashcardsPage.tsx
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { flashcardService } from '@/lib/services/flashcardService';
import { useAuth } from '@/context/AuthContext';

export default function FlashcardsPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  
  const { data: flashcards, isLoading } = useQuery({
    queryKey: ['flashcards', user?.id],
    queryFn: () => flashcardService.getUserFlashcards(user?.id || 'guest'),
    enabled: !!user
  });
  
  const generateFlashcardsMutation = useMutation({
    mutationFn: flashcardService.generateFlashcards,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['flashcards', user?.id] });
    }
  });
  
  const handleCreateFlashcards = async (formData) => {
    setIsGenerating(true);
    try {
      await generateFlashcardsMutation.mutateAsync({
        user_id: user?.id || 'guest',
        topic: formData.topic,
        num_cards: formData.numCards
      });
    } catch (error) {
      console.error('Flashcard generation error:', error);
    } finally {
      setIsGenerating(false);
    }
  };
  
  // Render flashcards list UI
}
```

## Phase 7: Progress & Dashboard Integration (Day 8)

**Step 15: Connect Dashboard Components**
```typescript
// Create frontend/client/src/lib/services/progressService.ts
import { apiRequest } from '../queryClient';

export const progressService = {
  getUserProgress: async (user_id: string) => {
    const response = await apiRequest('GET', `/progress/${user_id}`);
    return response.json();
  }
};

// Update frontend/client/src/pages/DashboardPage.tsx
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@/context/AuthContext';
import { sessionService } from '@/lib/services/sessionService';
import { progressService } from '@/lib/services/progressService';

export default function DashboardPage() {
  const { user } = useAuth();
  const [_, setLocation] = useLocation();
  
  const { data: recentSessions } = useQuery({
    queryKey: ['sessions', user?.id],
    queryFn: () => sessionService.getUserSessions(user?.id || 'guest'),
    enabled: !!user
  });
  
  const { data: progressData } = useQuery({
    queryKey: ['progress', user?.id],
    queryFn: () => progressService.getUserProgress(user?.id || 'guest'),
    enabled: !!user
  });
  
  const handleCreateQuickSession = () => {
    setLocation('/create-session');
  };
  
  const handleUploadDocuments = () => {
    setLocation('/documents');
  };
  
  const handleAskTutor = () => {
    setLocation('/chat');
  };
  
  // Render dashboard UI with ProgressSummary, RecentActivity, and RecommendedTopics
}
```

## Phase 8: Error Handling and Final Integration (Day 9)

**Step 16: Implement Global Error Handling**
```typescript
// Create frontend/client/src/lib/errorHandler.ts
import { toast } from '@/components/ui/use-toast';

export function handleApiError(error: any, customMessage?: string) {
  console.error('API Error:', error);
  
  const message = customMessage || 
    (error instanceof Error ? error.message : 'An unexpected error occurred');
  
  toast({
    title: 'Error',
    description: message,
    variant: 'destructive',
  });
  
  return null;
}
```

**Step 17: Update API Services with Error Handling**
```typescript
// Update the queryClient.ts file to include better error handling

import { API_BASE_URL } from './config';
import { handleApiError } from './errorHandler';

export async function apiRequest(
  method: string,
  endpoint: string,
  data?: unknown
): Promise<Response> {
  try {
    const url = `${API_BASE_URL}${endpoint}`;
    
    // Add auth token from localStorage if available
    const headers: HeadersInit = {};
    if (data && !(data instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }
    
    const authToken = localStorage.getItem('authToken');
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    const options: RequestInit = {
      method,
      headers,
      body: data instanceof FormData ? data : (data ? JSON.stringify(data) : undefined),
      credentials: 'include',
    };
    
    const response = await fetch(url, options);
    
    // Handle authentication errors
    if (response.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('authToken');
      window.location.href = '/login';
      throw new Error('Authentication required');
    }
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || `API request failed: ${response.status}`);
    }
    
    return response;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
}
```

## Phase 9: Authentication UI and Testing (Day 10)

**Step 18: Create Login/Register Components**
```typescript
// Create frontend/client/src/pages/LoginPage.tsx
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useLocation } from 'wouter';
import { useAuth } from '@/context/AuthContext';

const loginSchema = z.object({
  username: z.string().min(3),
  password: z.string().min(6),
});

export default function LoginPage() {
  const { login } = useAuth();
  const [_, setLocation] = useLocation();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const form = useForm<z.infer<typeof loginSchema>>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      username: '',
      password: ''
    }
  });
  
  const onSubmit = async (data: z.infer<typeof loginSchema>) => {
    setIsSubmitting(true);
    setError(null);
    
    try {
      await login(data.username, data.password);
      setLocation('/');
    } catch (error) {
      setError('Invalid username or password');
      console.error('Login error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  // Render login form UI
}
```

**Step 19: Add Authentication Routes and Guards**
```typescript
// Update frontend/client/src/App.tsx to include auth routes and guards
import { LoginPage } from './pages/LoginPage';
import { useAuth } from './context/AuthContext';

function ProtectedRoute({ component: Component }: { component: React.ComponentType }) {
  const { isAuthenticated, isLoading } = useAuth();
  const [_, setLocation] = useLocation();
  
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      setLocation('/login');
    }
  }, [isAuthenticated, isLoading, setLocation]);
  
  if (isLoading) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>;
  }
  
  return isAuthenticated ? <Component /> : null;
}

function Router() {
  return (
    <div className="flex h-screen overflow-hidden">
      <Switch>
        <Route path="/login" component={LoginPage} />
        
        <Route path="/">
          <Sidebar />
          <main className="flex-1 overflow-y-auto bg-gray-50 pb-16 md:pb-0">
            <Switch>
              <Route path="/" component={DashboardPage} />
              <Route path="/documents" component={DocumentsPage} />
              <Route path="/sessions" component={SessionsPage} />
              <Route path="/session/:id" component={StudySessionPage} />
              <Route path="/create-session" component={CreateSessionPage} />
              <Route path="/chat" component={ChatPage} />
              <Route path="/quizzes" component={QuizzesPage} />
              <Route path="/flashcards" component={FlashcardsPage} />
              <Route path="/verify" component={VerifyPage} />
              <Route component={NotFound} />
            </Switch>
          </main>
          <MobileNav />
        </Route>
      </Switch>
    </div>
  );
}
```

## Project Startup Guide

**Starting the Project**
A startup script (`start.sh`) has been created to run both backend and frontend services with a single command:

```bash
#!/bin/bash

# Start Study Buddy Backend and Frontend

echo "Starting Study Buddy services..."

# Function to handle cleanup on exit
cleanup() {
    echo "Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap for cleanup on SIGINT (Ctrl+C)
trap cleanup SIGINT

# Start Backend
echo "Starting FastAPI backend on http://localhost:8000..."
cd "$(dirname "$0")"
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Check if backend started successfully
sleep 2
if ! ps -p $BACKEND_PID > /dev/null; then
    echo "Failed to start backend!"
    exit 1
fi

# Start Frontend
echo "Starting React frontend..."
cd "$(dirname "$0")/frontend"
npm run dev &
FRONTEND_PID=$!

# Check if frontend started successfully
sleep 2
if ! ps -p $FRONTEND_PID > /dev/null; then
    echo "Failed to start frontend!"
    kill $BACKEND_PID
    exit 1
fi

echo "Both services started successfully!"
echo "Backend: http://localhost:8000"
echo "Frontend: Check the URL displayed in the terminal output (typically http://localhost:3000 or similar)"
echo "Press Ctrl+C to stop both services"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
```

To start both the backend and frontend:
```bash
./start.sh
```

## Integration Testing

To verify the integration between the frontend and backend, visit:
```
http://localhost:3000/verify
```

This page will attempt to connect to the backend's health check endpoint and display the connection status.
# Integration Guide: Adding the Study Buddy UI to Your Existing Backend

This guide will help you integrate the AI-powered Study Buddy UI with your existing backend in GitHub Codespaces.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Structure Setup](#project-structure-setup)
3. [Frontend Setup](#frontend-setup)
4. [API Integration](#api-integration)
5. [Backend Compatibility](#backend-compatibility)
6. [Running the Application](#running-the-application)
7. [GitHub Copilot Integration](#github-copilot-integration)
8. [Common Issues and Solutions](#common-issues-and-solutions)

## Prerequisites

Before starting the integration, ensure you have:

- GitHub Codespaces set up with your existing backend
- Node.js (v16.x or higher)
- Package manager (npm, yarn, or pnpm)
- Basic knowledge of React, TypeScript, and your backend technology
- Permission to install new dependencies in your project

## Project Structure Setup

You'll need to create a specific directory structure to integrate the Study Buddy UI with your existing backend. Here's the recommended approach:

1. **Create a dedicated frontend directory**:

```bash
mkdir -p study-buddy-ui/client
mkdir -p study-buddy-ui/shared
```

2. **Copy the files**:

Copy the following directories and files from this project to your new directories:

- Copy all contents from `client/` to `study-buddy-ui/client/`
- Copy `shared/schema.ts` to `study-buddy-ui/shared/schema.ts`
- Copy configuration files:
  - `components.json`
  - `postcss.config.js`
  - `tailwind.config.ts`
  - `vite.config.ts`

3. **Update your project's root package.json** to include necessary scripts:

```json
"scripts": {
  // Your existing scripts
  "dev:ui": "cd study-buddy-ui && vite",
  "build:ui": "cd study-buddy-ui && vite build",
  // Optional: Add a script to run both backend and frontend
  "dev:all": "concurrently \"npm run your-backend-script\" \"npm run dev:ui\""
}
```

## Frontend Setup

1. **Install dependencies**:

Navigate to your project root and run:

```bash
cd study-buddy-ui
npm install
```

This will install all the necessary dependencies listed in the package.json file, including React, Tailwind CSS, shadcn/ui components, and other UI libraries.

2. **Configure environment variables**:

Create a `.env` file in the `study-buddy-ui` directory:

```
VITE_API_BASE_URL=http://localhost:your-backend-port/api
```

Replace `your-backend-port` with the port your backend server is running on.

3. **Update the API client configuration**:

You'll need to modify the API client in `study-buddy-ui/client/src/lib/queryClient.ts` to point to your backend:

```typescript
// Add this import
import { apiBaseUrl } from './config';

// Update the apiRequest function
export async function apiRequest(
  input: RequestInfo | URL,
  init?: RequestInit
): Promise<Response> {
  // If the URL doesn't start with http(s):// or /, assume it's a relative path to the API
  const url = 
    typeof input === 'string' && !input.match(/^(https?:\/\/|\/)/i)
      ? `${apiBaseUrl}/${input}`
      : input;
  
  // Rest of the function...
}
```

4. **Create the config file** at `study-buddy-ui/client/src/lib/config.ts`:

```typescript
export const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api';
```

## API Integration

The Study Buddy UI expects specific API endpoints. You'll need to implement these endpoints in your backend or create adapter functions to map your existing endpoints to the expected format.

### Required API Endpoints

1. **Document Management**:
   - `POST /api/vectorstore/upload` - Upload documents
   - `GET /api/vectorstore/documents` - Retrieve all documents

2. **Session Management**:
   - `POST /api/session/quick` - Create a quick study session
   - `POST /api/session/execute` - Execute a session activity
   - `GET /api/session/user/:user_id` - Get sessions for a user

3. **Quiz Management**:
   - `POST /api/quiz/generate` - Generate a quiz
   - `GET /api/quiz/user/:user_id` - Get quizzes for a user

4. **Flashcard Management**:
   - `GET /api/flashcards` - Get flashcards (optionally filtered by user)
   - `POST /api/flashcard/generate` - Generate flashcards

5. **Chat**:
   - `POST /api/chat/chat` - Send a message to the AI assistant

### Adapter Pattern for API Integration

If your backend APIs don't match the expected endpoints, you can create an adapter layer in the frontend:

1. Create an `adapters` directory:

```bash
mkdir -p study-buddy-ui/client/src/lib/adapters
```

2. Implement adapter functions, for example:

```typescript
// study-buddy-ui/client/src/lib/adapters/sessionAdapter.ts

import { apiRequest } from '../queryClient';
import type { Session } from '../../../shared/schema';

// Your backend might have a different endpoint or data structure
export async function getUserSessions(userId: string): Promise<Session[]> {
  // If your backend has a different endpoint
  const response = await apiRequest(`your-actual-endpoint/sessions?userId=${userId}`);
  const data = await response.json();
  
  // Transform the data to match the expected format
  return data.map(item => ({
    session_id: item.id,
    user_id: userId,
    topic: item.subject,
    duration_minutes: item.durationInMinutes,
    created_at: item.createdDate,
    activities: item.tasks.map(task => ({
      type: mapTaskTypeToActivityType(task.type),
      duration_minutes: task.duration,
      description: task.description,
      parameters: task.params
    })),
    status: mapStatusValue(item.status),
    current_activity_index: item.currentTaskIndex || 0
  }));
}

// Helper function to map your backend's task types to the Study Buddy activity types
function mapTaskTypeToActivityType(taskType: string): 'introduction' | 'flashcard' | 'quiz' | 'summary' {
  const typeMap: Record<string, 'introduction' | 'flashcard' | 'quiz' | 'summary'> = {
    'intro': 'introduction',
    'cards': 'flashcard',
    'test': 'quiz',
    'recap': 'summary'
    // Add more mappings as needed
  };
  
  return typeMap[taskType] || 'introduction';
}

// Similar helper functions for other transformations
```

3. Update the API client functions to use these adapters:

```typescript
// study-buddy-ui/client/src/lib/api.ts

import { getUserSessions as adaptedGetUserSessions } from './adapters/sessionAdapter';

// Replace the implementation with your adapter
export const getUserSessions = adaptedGetUserSessions;
```

## Backend Compatibility

Ensure your backend can handle the data formats expected by the frontend:

### Data Types Compatibility

The Study Buddy UI expects specific data structures as defined in `shared/schema.ts`. Review this file to understand the expected data formats and ensure your backend can provide compatible data.

### Authentication and Authorization

If your backend uses authentication:

1. **Update API client to include auth tokens**:

```typescript
// study-buddy-ui/client/src/lib/queryClient.ts

export async function apiRequest(
  input: RequestInfo | URL,
  init?: RequestInit
): Promise<Response> {
  const authToken = localStorage.getItem('authToken'); // Or however you store tokens
  
  const headers = new Headers(init?.headers);
  if (authToken) {
    headers.set('Authorization', `Bearer ${authToken}`);
  }
  
  const updatedInit = {
    ...init,
    headers
  };
  
  // Rest of the function...
}
```

2. **Create authentication components** if needed:

```bash
mkdir -p study-buddy-ui/client/src/components/auth
touch study-buddy-ui/client/src/components/auth/LoginForm.tsx
```

3. **Update routing to handle authentication**:

```typescript
// study-buddy-ui/client/src/App.tsx

function Router() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('authToken'));
  
  // Add authentication check
  if (!isAuthenticated) {
    return <LoginPage onLogin={() => setIsAuthenticated(true)} />;
  }
  
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto bg-gray-50 pb-16 md:pb-0">
        <Switch>
          {/* Your routes */}
        </Switch>
      </main>
      <MobileNav />
    </div>
  );
}
```

## Running the Application

1. **Start your backend server** using your existing commands

2. **Start the frontend development server**:

```bash
npm run dev:ui
```

3. **Access the combined application**:

By default, the frontend will be available at `http://localhost:5173` and will make API calls to the URL specified in your `.env` file.

4. **Testing the integration**:

- Test document uploads
- Create a study session
- Try the chat functionality
- Generate quizzes and flashcards

## GitHub Copilot Integration

To help GitHub Copilot understand and assist with the integrated codebase:

1. **Provide clear file headers and documentation**:

Add descriptive comments at the top of key files:

```typescript
/**
 * Study Buddy UI - Chat Interface Component
 * 
 * This component provides an interactive chat interface for communicating with the AI tutor.
 * It supports different modes: tutor, quiz, chat, and flashcard.
 * 
 * @requires Backend API: POST /api/chat/chat
 * @requires Types from shared/schema.ts
 */
```

2. **Create a `.github/copilot` directory** with helpful information:

```bash
mkdir -p .github/copilot
touch .github/copilot/overview.md
```

3. **Add detailed information about the integration**:

Provide GitHub Copilot with context about how the frontend and backend work together in `overview.md`.

4. **Use consistent naming conventions**:

Ensure that naming is consistent across frontend and backend to help Copilot make connections between related files.

## Common Issues and Solutions

### CORS Issues

If you encounter CORS errors:

1. Configure your backend to allow requests from the frontend:

```javascript
// Express.js example
app.use(cors({
  origin: 'http://localhost:5173',
  credentials: true
}));
```

### API Endpoint Mismatches

If endpoints don't match exactly:

1. Use the adapter pattern described in the API Integration section
2. Or modify the frontend API client to match your backend endpoints

### Authentication Flow Issues

If you have problems with authentication:

1. Ensure tokens are properly stored and sent with requests
2. Check that your backend correctly validates tokens
3. Implement proper error handling for unauthorized requests

### Data Type Mismatches

If you see type errors or unexpected behavior:

1. Compare the data structure from your backend with what the frontend expects
2. Use adapter functions to transform data into the expected format
3. Update the TypeScript types if necessary

---

This integration guide should help you successfully add the Study Buddy UI to your existing backend. For further assistance, refer to the main README.md documentation or consult the GitHub Copilot comments within the code files.
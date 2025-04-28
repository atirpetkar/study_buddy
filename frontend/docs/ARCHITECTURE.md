# Technical Architecture: AI-Powered Study Buddy Application

This document provides an in-depth look at the technical architecture of the AI-powered Study Buddy application, explaining design patterns, component relationships, and data flow.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Design Patterns](#design-patterns)
3. [Component Hierarchy](#component-hierarchy)
4. [Data Flow](#data-flow)
5. [State Management](#state-management)
6. [API Integration](#api-integration)
7. [Authentication and Authorization](#authentication-and-authorization)
8. [Performance Considerations](#performance-considerations)

## Architecture Overview

The Study Buddy application follows a modern client-server architecture with a clear separation of concerns:

```
                                ┌───────────────────┐
                                │                   │
                                │    Client Layer   │
                                │    (React App)    │
                                │                   │
                                └─────────┬─────────┘
                                          │
                                          │ HTTP/REST
                                          │
                                ┌─────────▼─────────┐
                                │                   │
                                │   Server Layer    │
                                │  (Express/Node)   │
                                │                   │
                                └─────────┬─────────┘
                                          │
                                          │ ORM
                                          │
                                ┌─────────▼─────────┐
                                │                   │
                                │  Persistence Layer│
                                │   (PostgreSQL)    │
                                │                   │
                                └───────────────────┘
```

### Key Components

1. **Client Layer**:
   - React with TypeScript for the UI
   - TanStack Query for data fetching and caching
   - Tailwind CSS and shadcn/ui for styling
   - Wouter for client-side routing

2. **Server Layer**:
   - Express.js server handling HTTP requests
   - Route handlers for API endpoints
   - Business logic for processing learning activities
   - File upload handling with Multer

3. **Persistence Layer**:
   - PostgreSQL database (Drizzle ORM)
   - Structured data storage (users, documents, sessions, quizzes, flashcards)
   - In-memory storage option for development or simple deployments

## Design Patterns

The application implements several design patterns to maintain clean, maintainable code:

### 1. Repository Pattern

The storage interface in `server/storage.ts` implements the Repository pattern, providing a clean abstraction over data access:

```typescript
export interface IStorage {
  // User methods
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  
  // Document methods
  createDocument(document: InsertDocument): Promise<Document>;
  getDocument(id: number): Promise<Document | undefined>;
  getAllDocuments(): Promise<Document[]>;
  
  // Additional methods...
}
```

This allows for:
- Swapping the underlying data store (e.g., moving from in-memory to PostgreSQL)
- Mocking for testing
- Centralizing data access logic

### 2. Facade Pattern

The API client in `client/src/lib/api.ts` implements the Facade pattern, providing a simplified interface to the complex backend API:

```typescript
export const uploadDocuments = async (files: FileList) => {
  // Complex implementation details hidden behind a simple interface
};

export const createQuickSession = async (data: { user_id: string; topic: string; duration_minutes: number }) => {
  // Complex implementation details hidden behind a simple interface
};
```

### 3. Container/Presenter Pattern

Components are generally structured following the Container/Presenter pattern:
- Container components handle data fetching, state, and business logic
- Presenter components focus on rendering UI elements based on props

Example:
```typescript
// Container component
export default function DocumentsPage() {
  const [isUploading, setIsUploading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  
  const { data: documents, isLoading, error, refetch } = useQuery({
    queryKey: ['/api/vectorstore/documents'],
    queryFn: getDocuments,
  });
  
  const handleFileUpload = async (files: FileList) => {
    setIsUploading(true);
    try {
      await uploadDocuments(files);
      refetch();
    } catch (error) {
      console.error("Upload error:", error);
    } finally {
      setIsUploading(false);
    }
  };
  
  return (
    <div className="container p-4 mx-auto">
      <h1 className="mb-6 text-2xl font-bold">Document Library</h1>
      
      <DocumentUpload onUpload={handleFileUpload} isUploading={isUploading} />
      
      <DocumentList
        documents={documents?.documents || []}
        isLoading={isLoading}
        error={error as Error}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
      />
    </div>
  );
}

// Presenter component
export default function DocumentList({
  documents,
  isLoading,
  error,
  searchQuery,
  onSearchChange,
}: DocumentListProps) {
  // UI rendering only
}
```

### 4. Module Pattern

The application organizes code into modules with clear responsibilities:
- Pages represent complete views/routes
- Components are reusable UI elements
- Hooks encapsulate reusable logic
- Utilities provide helper functions

## Component Hierarchy

The frontend component hierarchy follows a logical structure:

```
App
│
├── Router
│   ├── Sidebar
│   ├── Main Content
│   │   ├── DashboardPage
│   │   │   ├── ProgressSummary
│   │   │   ├── RecentActivity
│   │   │   └── RecommendedTopics
│   │   │
│   │   ├── DocumentsPage
│   │   │   ├── DocumentUpload
│   │   │   └── DocumentList
│   │   │
│   │   ├── SessionsPage
│   │   │   ├── SessionActivity (list)
│   │   │   └── CreateSessionLink
│   │   │
│   │   ├── StudySessionPage
│   │   │   ├── ActivityIntroduction
│   │   │   ├── ActivityFlashcard
│   │   │   ├── ActivityQuiz
│   │   │   └── ActivitySummary
│   │   │
│   │   ├── CreateSessionPage
│   │   │   └── CreateSession
│   │   │
│   │   ├── ChatPage
│   │   │   └── ChatInterface
│   │   │
│   │   ├── QuizzesPage
│   │   │   └── QuizPlayer
│   │   │
│   │   └── FlashcardsPage
│   │       └── FlashcardPlayer
│   │
│   └── MobileNav
│
└── Toaster (notifications)
```

### Component Responsibilities

- **Layout Components**: Provide the overall structure and navigation
  - `Sidebar`: Main navigation for desktop
  - `MobileNav`: Mobile-optimized navigation 

- **Page Components**: Container components that fetch data and coordinate child components
  - Each page handles its own data fetching and state management

- **Feature Components**: Implement specific application features
  - `DocumentUpload`: Handle file selection and uploading
  - `ChatInterface`: Manage chat conversation and AI interactions
  - `ActivityQuiz`: Render and control interactive quizzes

- **UI Components**: Reusable, presentation-focused components (from shadcn/ui)
  - `Button`, `Card`, `Input`, etc.

## Data Flow

Data flows through the application following a predictable pattern:

1. **User Interaction** → Frontend Component
2. **Component Event Handler** → API Client
3. **API Client** → Backend API
4. **API Handler** → Storage Interface
5. **Storage Interface** → Database
6. **Response** → Component State → UI Update

Example flow for creating a study session:

```
User submits form in CreateSession component
↓
handleSubmit() captures form data
↓
createQuickSession() API client function is called with form data
↓
API call to POST /api/session/quick with session data
↓
Server validates data with Zod schema
↓
storage.createSession() creates session in database
↓
Response returns session details
↓
React Query invalidates sessions cache
↓
UI updates to show new session
↓
User is redirected to the new session page
```

## State Management

The application uses a combination of state management approaches:

### 1. Server State

TanStack Query (React Query) manages server state:
- Fetching data from the API
- Caching responses
- Handling loading and error states
- Refetching when needed
- Mutations with cache invalidation

Example:
```typescript
// Fetching data
const { data, isLoading, error } = useQuery({
  queryKey: ['/api/session/user', userId],
  queryFn: () => getUserSessions(userId)
});

// Mutation with cache invalidation
const createSessionMutation = useMutation({
  mutationFn: createQuickSession,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['/api/session/user', userId] });
  }
});
```

### 2. Component State

React's useState and useReducer manage local component state:
- Form inputs and validation
- UI state (open/closed modals, active tabs)
- Component-specific logic

Example:
```typescript
const [currentIndex, setCurrentIndex] = useState(0);
const [showHint, setShowHint] = useState(false);
```

### 3. Form State

React Hook Form manages form state:
- Input values and touched status
- Form validation with Zod
- Form submission handling

Example:
```typescript
const form = useForm<z.infer<typeof sessionFormSchema>>({
  resolver: zodResolver(sessionFormSchema),
  defaultValues: {
    topic: "",
    duration_minutes: 30,
  },
});
```

## API Integration

The frontend integrates with the backend API through several layers:

### 1. Base API Client

The `apiRequest` function in `client/src/lib/queryClient.ts` provides a foundation for all API calls:
- Handling request/response formatting
- Error processing
- Authentication headers

### 2. API Functions

Specific API functions in `client/src/lib/api.ts` build on the base client:
- Implementing endpoint-specific logic
- Handling file uploads
- Formatting request data

### 3. React Query Integration

TanStack Query hooks connect API functions to components:
- `useQuery` for data fetching
- `useMutation` for data mutations
- Query invalidation for cache management

## Authentication and Authorization

The application implements a simple authentication flow:

1. **User Authentication**:
   - Username/password based authentication (can be extended)
   - Session management with Express session
   - Authorization checks on protected routes

2. **API Authorization**:
   - Route middleware checks session for user ID
   - Resources filtered by user ID where appropriate
   - Simple role-based access (can be extended)

## Performance Considerations

The application includes several performance optimizations:

### 1. Query Caching

TanStack Query provides efficient data caching:
- Reduces duplicate API calls
- Implements stale-while-revalidate pattern
- Supports background refetching

### 2. Code Splitting

The application can implement code splitting to reduce initial load time:
- Route-based splitting for page components
- Dynamic imports for large components

### 3. Optimized Rendering

React's virtual DOM and careful component design minimize unnecessary re-renders:
- Proper use of dependency arrays in hooks
- Memoization where appropriate
- Avoiding prop drilling

### 4. Pagination

For large data sets, the API implements pagination:
- Limit/offset parameters
- Cursor-based pagination for efficiency
- Loading states during pagination

---

This architecture document provides a technical overview of the Study Buddy application's design and implementation. Developers can use this as a guide to understand how the various components work together and the patterns used throughout the codebase.
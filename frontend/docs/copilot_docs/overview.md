# GitHub Copilot Guide: AI-Powered Study Buddy Application

This guide is designed specifically to help GitHub Copilot understand the AI-powered Study Buddy application codebase. It provides context about design patterns, coding conventions, and functional components to improve code suggestions.

## Codebase Overview

The Study Buddy application is an AI-powered learning platform that processes study materials and creates personalized learning experiences through quizzes, flashcards, and guided study sessions. 

### Primary Technologies

- **Frontend**: React with TypeScript, Tailwind CSS, shadcn/ui components
- **Backend**: Node.js/Express with TypeScript
- **Data Management**: Drizzle ORM with PostgreSQL/in-memory storage
- **State Management**: TanStack Query (React Query) for server state, React hooks for local state
- **Form Handling**: React Hook Form with Zod validation
- **Routing**: wouter for client-side routing

## Code Organization Patterns

The codebase follows these organizational patterns that Copilot should consider when suggesting code:

### 1. Component Organization

Components follow a predictable structure:
```typescript
// Import statements
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Component } from "@/components/ui/component";

// Type definitions
interface ComponentProps {
  prop1: string;
  prop2: number;
}

// Component definition
export default function ComponentName({ prop1, prop2 }: ComponentProps) {
  // State hooks
  const [state, setState] = useState(initialValue);
  
  // Data fetching
  const { data, isLoading } = useQuery({
    queryKey: ['/api/endpoint'],
    queryFn: fetchFunction
  });
  
  // Event handlers
  const handleEvent = () => {
    // Logic
  };
  
  // Render logic with early returns for loading/error states
  if (isLoading) return <LoadingComponent />;
  
  return (
    <div className="tailwind-classes">
      {/* Component JSX */}
    </div>
  );
}
```

### 2. API Client Pattern

API client functions follow this pattern:
```typescript
export const apiFunction = async (params: ParamType): Promise<ReturnType> => {
  try {
    const response = await apiRequest('endpoint', {
      method: 'POST',
      body: JSON.stringify(params)
    });
    
    if (!response.ok) {
      throw new Error('Error message');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error in apiFunction:', error);
    throw error;
  }
};
```

### 3. Form Handling Pattern

Forms use React Hook Form with Zod validation:
```typescript
// Schema definition
const formSchema = z.object({
  field1: z.string().min(3).max(50),
  field2: z.number().min(1).max(100)
});

// Form hook setup
const form = useForm<z.infer<typeof formSchema>>({
  resolver: zodResolver(formSchema),
  defaultValues: {
    field1: "",
    field2: 1
  }
});

// Form submission
const onSubmit = (data: z.infer<typeof formSchema>) => {
  // Handle submission
};

// JSX pattern
return (
  <Form {...form}>
    <form onSubmit={form.handleSubmit(onSubmit)}>
      {/* Form fields */}
      <FormField
        control={form.control}
        name="field1"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Field Label</FormLabel>
            <FormControl>
              <Input {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
      
      <Button type="submit">Submit</Button>
    </form>
  </Form>
);
```

## Important Type Definitions

The application uses many TypeScript types that are important to understand:

### Core Data Types

```typescript
// User
type User = {
  id: number;
  username: string;
  password: string; // Hashed, not plain text
};

// Document
type Document = {
  id: number;
  filename: string;
  filetype: string;
  upload_time: Date;
  chunk_count: number;
  user_id: number;
};

// Session
type Session = {
  id: number;
  session_id: string;
  user_id: string;
  topic: string;
  duration_minutes: number;
  created_at: Date;
  activities: Activity[];
  status: string;
  current_activity_index: number;
};

// Activity
type Activity = {
  type: 'introduction' | 'flashcard' | 'quiz' | 'summary';
  duration_minutes: number;
  description: string;
  parameters: Record<string, any>;
};

// Quiz
type Quiz = {
  id: number;
  quiz_id: string;
  user_id: string;
  topic: string;
  questions: Question[];
  metadata: Record<string, any>;
  created_at: Date;
};

// Question
type Question = {
  id: string;
  text: string;
  options: {
    A: string;
    B: string;
    C: string;
    D: string;
  };
  correct_answer: string;
  explanation: string;
};

// Flashcard
type Flashcard = {
  id: number;
  flashcard_id: string;
  user_id: string;
  topic: string;
  cards: Card[];
  metadata: Record<string, any>;
  created_at: Date;
};

// Card
type Card = {
  id: string;
  front: string;
  back: string;
};
```

### Component-Specific Types

```typescript
// Message (for ChatInterface)
type Message = {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  timestamp: Date;
  context_used?: string[];
};

// Progress Data (for ProgressSummary)
type ProgressData = {
  studyTime: number;
  studyTimePercentage: number;
  quizzesCompleted: number;
  quizzesPercentage: number;
  flashcardsMastered: number;
  flashcardsPercentage: number;
};

// Activity (for RecentActivity)
type Activity = {
  type: string;
  title: string;
  time: string;
  duration?: string;
  detail?: string;
  icon: string;
  iconBg: string;
  iconColor: string;
};
```

## API Endpoints

When suggesting API calls, be aware of these endpoint patterns:

### Document Management
- `GET /api/vectorstore/documents`: Get all documents
- `POST /api/vectorstore/upload`: Upload documents (uses FormData)

### Sessions
- `GET /api/session/user/:user_id`: Get sessions for a user
- `POST /api/session/quick`: Create a quick study session
- `POST /api/session/execute`: Execute a session activity

### Quizzes
- `GET /api/quiz/user/:user_id`: Get quizzes for a user
- `POST /api/quiz/generate`: Generate a quiz

### Flashcards
- `GET /api/flashcards?user_id=:user_id`: Get flashcards for a user
- `POST /api/flashcard/generate`: Generate flashcards

### Chat
- `POST /api/chat/chat`: Send a message to the AI assistant

## Common Tailwind Patterns

The application uses these common Tailwind patterns that Copilot should consider:

### Layout Patterns
```
container mx-auto px-4 py-6            // Main container
grid grid-cols-1 md:grid-cols-2 gap-4  // Responsive grid
flex items-center justify-between       // Horizontal layout with space between
flex flex-col space-y-4                 // Vertical stack with spacing
```

### Component Styling
```
// Card styling
rounded-lg border bg-card p-4 shadow-sm

// Button variants
bg-primary text-primary-foreground hover:bg-primary/90  // Primary button
bg-secondary text-secondary-foreground hover:bg-secondary/90  // Secondary button
border border-input bg-background hover:bg-accent hover:text-accent-foreground  // Outline button

// Form elements
w-full rounded-md border border-input bg-transparent px-3 py-2  // Input fields
```

### Responsive Patterns
```
hidden md:block               // Hide on mobile, show on desktop
block md:hidden               // Show on mobile, hide on desktop
flex-col md:flex-row          // Vertical on mobile, horizontal on desktop
text-sm md:text-base lg:text-lg  // Responsive text sizing
```

## Debugging Tips

When suggesting debugging code, consider these patterns:

### Console Logging

```typescript
console.log("Component rendered", { props, state });
console.error("API error:", error);

// For complex objects
console.log("Session data:", JSON.stringify(session, null, 2));
```

### Error Handling

```typescript
try {
  // Risky code
} catch (error) {
  console.error("Operation failed:", error);
  toast({
    title: "Error",
    description: error instanceof Error ? error.message : "An unknown error occurred",
    variant: "destructive"
  });
}
```

### API Debugging

```typescript
// Add to apiRequest function for debugging
console.log(`API Request: ${method} ${url}`, body);
const response = await fetch(url, options);
console.log(`API Response: ${response.status}`, await response.clone().json());
```

## Testing Approaches

When suggesting tests, consider these patterns:

### Component Testing

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Component from './Component';

describe('Component', () => {
  it('renders correctly', () => {
    render(<Component prop1="value" />);
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });
  
  it('handles user interaction', async () => {
    render(<Component prop1="value" />);
    await userEvent.click(screen.getByRole('button', { name: 'Button Text' }));
    expect(screen.getByText('Result Text')).toBeInTheDocument();
  });
});
```

### API Testing

```typescript
import { apiFunction } from './api';
import fetchMock from 'jest-fetch-mock';

describe('API function', () => {
  beforeEach(() => {
    fetchMock.resetMocks();
  });
  
  it('fetches data successfully', async () => {
    fetchMock.mockResponseOnce(JSON.stringify({ data: 'value' }));
    const result = await apiFunction(params);
    expect(result).toEqual({ data: 'value' });
    expect(fetchMock).toHaveBeenCalledWith('endpoint', expect.objectContaining({
      method: 'POST'
    }));
  });
  
  it('handles errors correctly', async () => {
    fetchMock.mockRejectOnce(new Error('API error'));
    await expect(apiFunction(params)).rejects.toThrow('API error');
  });
});
```

## Workflow Patterns

### Component Creation Workflow

When suggesting new components, follow this workflow:
1. Define the component's props interface
2. Set up necessary state with React hooks
3. Add data fetching with React Query if needed
4. Implement event handlers
5. Return JSX with proper Tailwind styling

### Feature Implementation Workflow

When implementing a new feature, follow this pattern:
1. Define data types in `shared/schema.ts`
2. Implement backend API endpoints in `server/routes.ts`
3. Create API client functions in `client/src/lib/api.ts`
4. Build React components in `client/src/components/`
5. Add page component in `client/src/pages/`
6. Update routing in `client/src/App.tsx`

## Pitfalls to Avoid

When making suggestions, help avoid these common pitfalls:

1. **Nesting anchor tags**: This causes HTML validation errors
2. **Missing key props**: Always include key props in mapped arrays
3. **Improper form validation**: Always use Zod schemas for validation
4. **Forgetting to invalidate queries**: Always invalidate queries after mutations
5. **Direct DOM manipulation**: Prefer React's controlled component pattern
6. **Not handling loading states**: Always handle loading and error states
7. **Incorrect Tailwind usage**: Follow the project's existing Tailwind patterns

---

This guide should help GitHub Copilot generate more accurate and helpful code suggestions for the AI-powered Study Buddy application. For more detailed information, refer to the main documentation files.
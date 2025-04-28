# AI Study Buddy Quick Start Guide (for GitHub Copilot)

This quick start guide is designed to help you work efficiently with the AI Study Buddy codebase using GitHub Copilot. It provides essential context and key commands to get you started quickly.

## Project Purpose

The AI Study Buddy is an interactive learning application that:
- Processes uploaded study materials
- Creates personalized study sessions with various activity types
- Generates quizzes and flashcards based on content
- Provides an AI chat interface for study assistance
- Tracks learning progress over time

## Key Commands

### Setup and Installation

```bash
# Clone the repository
git clone <repository-url>
cd study-buddy

# Install dependencies
npm install

# Start development server
npm run dev
```

### Database Commands (if using PostgreSQL)

```bash
# Apply database migrations
npm run db:push

# Reset database (during development)
npm run db:reset
```

### Build and Production

```bash
# Build for production
npm run build

# Start production server
npm run start
```

## File Structure Quick Reference

When using GitHub Copilot, keep these key file locations in mind:

```
/client/src/components/  # React components
/client/src/pages/       # Page components
/client/src/lib/         # Utilities and API clients
/server/routes.ts        # API endpoints
/server/storage.ts       # Data storage interface
/shared/schema.ts        # Data models and types
```

## Common React Patterns

GitHub Copilot works best when you follow these patterns:

### Component Creation

```typescript
// Start a new component with:
export default function ComponentName({ 
  // Type your props here and Copilot will suggest completions
}) {
  // Add state hooks
  const [state, setState] = useState(initialValue);
  
  // Add effect hooks
  useEffect(() => {
    // Copilot will suggest effect logic
  }, [dependencies]);
  
  return (
    // Start typing JSX and Copilot will suggest completions
  );
}
```

### Data Fetching

```typescript
// Start a query with:
const { data, isLoading, error } = useQuery({
  // Copilot will suggest the rest
});

// Start a mutation with:
const mutation = useMutation({
  // Copilot will suggest the rest
});
```

### Form Creation

```typescript
// Start form validation with:
const formSchema = z.object({
  // Copilot will suggest validation rules
});

// Start form hook with:
const form = useForm<z.infer<typeof formSchema>>({
  // Copilot will suggest the rest
});
```

## Working with Types

GitHub Copilot can help define and use these common types:

### Define a New Type

```typescript
// Start with:
type MyComponentProps = {
  // Copilot will suggest properties based on usage
};
```

### Using Existing Types

```typescript
// Import types:
import type { Session, Activity } from '@/shared/schema';

// Use in function signatures:
function processSession(session: Session): Activity[] {
  // Copilot will suggest implementation
}
```

## API Patterns

GitHub Copilot can help you work with the API:

### Create API Client Function

```typescript
// Start with:
export const myApiFunction = async (params: ParamType): Promise<ReturnType> => {
  // Copilot will suggest implementation
};
```

### API Usage in Components

```typescript
// Start with handling a form submission:
const handleSubmit = async (data) => {
  try {
    // Copilot will suggest API call and error handling
  } catch (error) {
    // Copilot will suggest error handling
  }
};
```

## UI Component Usage

GitHub Copilot can help you implement UI components:

### Card Component

```tsx
// Start with:
<Card>
  <CardHeader>
    // Copilot will suggest content
  </CardHeader>
  <CardContent>
    // Copilot will suggest content
  </CardContent>
</Card>
```

### Dialog Component

```tsx
// Start with:
const [open, setOpen] = useState(false);

// Then:
<Dialog open={open} onOpenChange={setOpen}>
  // Copilot will suggest dialog content
</Dialog>
```

### Form Component

```tsx
// Start with:
<Form {...form}>
  <form onSubmit={form.handleSubmit(onSubmit)}>
    // Copilot will suggest form fields
  </form>
</Form>
```

## Tips for Effective Copilot Use

1. **Start with type definitions**: Define interfaces and types first to get better suggestions
2. **Use consistent naming**: Follow project naming conventions for better predictions
3. **Write descriptive comments**: Comments help Copilot understand your intent
4. **Accept partial suggestions**: You can accept part of a suggestion and continue typing
5. **Look for patterns**: Study existing code to understand the patterns Copilot will follow

## Debugging Prompts

These comments can help Copilot generate debugging code:

```typescript
// Generate a comprehensive debug log for this component
console.log("Debug ComponentName:", { props, state, data });

// Generate API request logging
console.log("API Request:", { endpoint, method, body });

// Generate API response logging
console.log("API Response:", { status, data });

// Generate error handling for this try/catch block
try {
  // Your code
} catch (error) {
  // Copilot will suggest error handling
}
```

## Testing Prompts

These comments can help Copilot generate test code:

```typescript
// Generate a test for this component
describe('ComponentName', () => {
  // Copilot will suggest test cases
});

// Generate a test for this API function
describe('apiFunction', () => {
  // Copilot will suggest test cases
});

// Generate a test for this utility function
describe('utilityFunction', () => {
  // Copilot will suggest test cases
});
```

---

For more detailed information, refer to the main README.md documentation and the detailed Copilot guide in `/.github/copilot/overview.md`.
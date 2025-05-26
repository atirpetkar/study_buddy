import { useToast } from "@/hooks/use-toast";

/**
 * Centralized error handler for API errors
 * 
 * @param error The error object
 * @param customMessage Optional custom message to display
 * @returns null (for convenience in catch blocks)
 */
export function handleApiError(error: any, customMessage?: string) {
  console.error('API Error:', error);
  
  // Format error message
  const message = customMessage || 
    (error instanceof Error ? error.message : 'An unexpected error occurred');
  
  // Show toast notification using the hook (note: this requires a component context)
  const { toast } = useToast();
  toast({
    title: 'Error',
    description: message,
    variant: 'destructive',
  });
  
  // Return null for convenient use in catch blocks
  return null;
}

/**
 * Wrapper for async functions that handles errors automatically
 * Note: This should be used within a component that has access to the toast context
 * 
 * @param fn The async function to wrap
 * @param errorMessage Optional custom error message
 * @returns A new function that catches errors and handles them
 */
export function withErrorHandling<T extends (...args: any[]) => Promise<any>>(
  fn: T,
  errorMessage?: string,
  toastFn?: (props: any) => void
): (...args: Parameters<T>) => Promise<ReturnType<T> | null> {
  return async (...args: Parameters<T>) => {
    try {
      return await fn(...args);
    } catch (error) {
      console.error('API Error:', error);
      
      // Format error message
      const message = errorMessage || 
        (error instanceof Error ? error.message : 'An unexpected error occurred');
      
      // Use provided toast function if available
      if (toastFn) {
        toastFn({
          title: 'Error',
          description: message,
          variant: 'destructive',
        });
      }
      
      return null;
    }
  };
}

/**
 * Centralized error handler for API errors
 * 
 * @param error The error object
 * @param customMessage Optional custom message to display
 * @returns Formatted error message
 */
export function formatErrorMessage(error: any, customMessage?: string): string {
  // Format error message
  return customMessage || 
    (error instanceof Error ? error.message : 'An unexpected error occurred');
}

/**
 * Logger for API errors
 * 
 * @param error The error object
 * @param context Additional context information
 */
export function logApiError(error: any, context?: string) {
  console.error(`API Error${context ? ` [${context}]` : ''}:`, error);
} 
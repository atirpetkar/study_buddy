// Base URL for API requests
// In development, this points to the backend API
// In production, this could be configured to point to your deployed API

export const API_BASE_URL = '/api';

// JWT-related config
export const TOKEN_STORAGE_KEY = 'authToken';

// Backend configuration
export const BACKEND_PORT = 8000;

// User configuration
// In a real app, this would come from authentication
// Using "qwe@gmail.com" for all API requests for consistency
export const DEFAULT_USER_ID = 'qwe@gmail.com';

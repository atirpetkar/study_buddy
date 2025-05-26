import { apiRequest } from '../queryClient';
import { API_BASE_URL } from '../config';

export interface User {
  id: string;
  email: string;
}

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
  
  register: async (email: string, password: string) => {
    // In a production app, you would never send a plain password to the server
    // This is just for demonstration purposes
    const hashedPassword = password; // In reality, the backend should handle hashing
    
    const response = await apiRequest('POST', '/users/', {
      email,
      hashed_password: hashedPassword
    });
    
    return response.json();
  },
  
  getCurrentUser: async () => {
    try {
      const response = await apiRequest('GET', '/users/me');
      return response.json();
    } catch (error) {
      console.error('Error fetching current user:', error);
      return null;
    }
  },
  
  logout: async () => {
    localStorage.removeItem('authToken');
    // If you have a logout endpoint on your backend:
    // await apiRequest('POST', '/users/logout');
  }
};
import React, { createContext, useState, useEffect, useContext } from 'react';
import { API_BASE_URL } from '../lib/config';

export interface User {
  id: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  login: async () => {},
  logout: () => {},
  isAuthenticated: false,
  isLoading: true
});

// Separate the hook definition
function useAuthContext() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

export const useAuth = useAuthContext;

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Initialize with a hardcoded user for now
  const [user, setUser] = useState<User | null>({
    id: "hardcoded-user-id",
    email: "qwe@gmail.com"
  });
  
  // Set isLoading to false since we're using a hardcoded user
  const [isLoading, setIsLoading] = useState(false);

  // Disable actual authentication for now
  const login = async (email: string, password: string) => {
    console.log('Login bypassed, using hardcoded user');
    // Set the hardcoded user
    setUser({
      id: "hardcoded-user-id",
      email: "qwe@gmail.com"
    });
    // Mock token for any code that might check for it
    localStorage.setItem('authToken', 'mock-token-for-development');
  };

  const logout = () => {
    // Keep the hardcoded user even on logout for now
    console.log('Logout bypassed, keeping hardcoded user');
  };

  return (
    <AuthContext.Provider value={{
      user,
      login,
      logout,
      isAuthenticated: true, // Always authenticated
      isLoading: false       // Never loading
    }}>
      {children}
    </AuthContext.Provider>
  );
};
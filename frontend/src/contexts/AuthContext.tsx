import React, { createContext, useContext, useState, ReactNode } from 'react';

export type UserRole = 'employee' | 'team_leader';

export interface User {
  id: string;
  email: string;
  name: string;
  department: string;
  role: UserRole;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (name: string, email: string, department: string, password: string) => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Mock users for demonstration
const mockUsers: User[] = [
  {
    id: '1',
    email: 'employee@managery.com',
    name: 'John Employee',
    department: 'Engineering',
    role: 'employee',
  },
  {
    id: '2',
    email: 'leader@managery.com',
    name: 'Sarah Leader',
    department: 'Engineering',
    role: 'team_leader',
  },
];

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 800));
    
    const foundUser = mockUsers.find(u => u.email === email);
    
    if (!foundUser || password !== 'password123') {
      setError('Invalid email or password');
      setIsLoading(false);
      throw new Error('Invalid credentials');
    }
    
    setUser(foundUser);
    setIsLoading(false);
  };

  const register = async (name: string, email: string, department: string, password: string) => {
    setIsLoading(true);
    setError(null);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 800));
    
    const newUser: User = {
      id: String(mockUsers.length + 1),
      email,
      name,
      department,
      role: 'employee',
    };
    
    mockUsers.push(newUser);
    setUser(newUser);
    setIsLoading(false);
  };

  const logout = () => {
    setUser(null);
    setError(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, register, isLoading, error }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// import React, { createContext, useContext, useState, ReactNode } from 'react';

// export type UserRole = 'employee' | 'team_leader';

// export interface User {
//   id: string;
//   email: string;
//   name: string;
//   department: string;
//   role: UserRole;
// }

// interface AuthContextType {
//   user: User | null;
//   login: (email: string, password: string) => Promise<void>;
//   logout: () => void;
//   register: (name: string, email: string, department: string, password: string) => Promise<void>;
//   isLoading: boolean;
//   error: string | null;
// }

// const AuthContext = createContext<AuthContextType | undefined>(undefined);

// // Mock users for demonstration
// const mockUsers: User[] = [
//   {
//     id: '1',
//     email: 'employee@managery.com',
//     name: 'John Employee',
//     department: 'Engineering',
//     role: 'employee',
//   },
//   {
//     id: '2',
//     email: 'leader@managery.com',
//     name: 'Sarah Leader',
//     department: 'Engineering',
//     role: 'team_leader',
//   },
// ];

// export function AuthProvider({ children }: { children: ReactNode }) {
//   const [user, setUser] = useState<User | null>(null);
//   const [isLoading, setIsLoading] = useState(false);
//   const [error, setError] = useState<string | null>(null);

//   const login = async (email: string, password: string) => {
//     setIsLoading(true);
//     setError(null);

//     // Simulate API call
//     await new Promise(resolve => setTimeout(resolve, 800));

//     const foundUser = mockUsers.find(u => u.email === email);

//     if (!foundUser || password !== 'password123') {
//       setError('Invalid email or password');
//       setIsLoading(false);
//       throw new Error('Invalid credentials');
//     }

//     setUser(foundUser);
//     setIsLoading(false);
//   };

//   const register = async (name: string, email: string, department: string, password: string) => {
//     setIsLoading(true);
//     setError(null);

//     // Simulate API call
//     await new Promise(resolve => setTimeout(resolve, 800));

//     const newUser: User = {
//       id: String(mockUsers.length + 1),
//       email,
//       name,
//       department,
//       role: 'employee',
//     };

//     mockUsers.push(newUser);
//     setUser(newUser);
//     setIsLoading(false);
//   };

//   const logout = () => {
//     setUser(null);
//     setError(null);
//   };

//   return (
//     <AuthContext.Provider value={{ user, login, logout, register, isLoading, error }}>
//       {children}
//     </AuthContext.Provider>
//   );
// }

// export function useAuth() {
//   const context = useContext(AuthContext);
//   if (context === undefined) {
//     throw new Error('useAuth must be used within an AuthProvider');
//   }
//   return context;
// }

// src/contexts/AuthContext.tsx
// src/contexts/AuthContext.tsx
import React, {
  createContext,
  useContext,
  useState,
  ReactNode,
  useEffect,
  useCallback,
} from "react";
import { apiFetch } from "@/lib/api";

export type UserRole = "employee" | "team_leader";

export interface User {
  id: string;
  email: string;
  name?: string;
  department?: string;
  role: UserRole;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (
    name: string,
    email: string,
    department: string,
    password: string
  ) => Promise<void>;
  isLoading: boolean;
  error: string | null;
  getAuthHeaders: () => { Authorization?: string };
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);
const STORAGE_KEY = "auth_token";

function parseJwt(token: string | null) {
  if (!token) return null;
  try {
    const base64 = token.split(".")[1];
    if (!base64) return null;
    const payloadStr = decodeURIComponent(
      atob(base64)
        .split("")
        .map(function (c) {
          return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
        })
        .join("")
    );
    return JSON.parse(payloadStr);
  } catch {
    return null;
  }
}

function tokenExpired(token: string | null) {
  const payload = parseJwt(token);
  if (!payload || !payload.exp) return true;
  return Date.now() > payload.exp * 1000;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => {
    try {
      return localStorage.getItem(STORAGE_KEY);
    } catch {
      return null;
    }
  });
  const [user, setUser] = useState<User | null>(() => {
    const payload = parseJwt(localStorage.getItem(STORAGE_KEY));
    if (payload && payload.id) {
      return {
        id: payload.id,
        email: payload.email,
        name: payload.name,
        department: payload.department,
        role: payload.role,
      } as User;
    }
    return null;
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      setUser(null);
      try { localStorage.removeItem(STORAGE_KEY); } catch { }
      return;
    }
    if (tokenExpired(token)) {
      setToken(null);
      setUser(null);
      try { localStorage.removeItem(STORAGE_KEY); } catch { }
      return;
    }
    const payload = parseJwt(token);
    if (payload && payload.id) {
      setUser({
        id: payload.id,
        email: payload.email,
        name: payload.name,
        department: payload.department,
        role: payload.role,
      } as User);
    }
  }, [token]);

  const setTokenAndStore = useCallback((t: string | null) => {
    setToken(t);
    try {
      if (t) localStorage.setItem(STORAGE_KEY, t);
      else localStorage.removeItem(STORAGE_KEY);
    } catch { }
  }, []);

  const getAuthHeaders = useCallback(() => {
    if (!token) return {};
    return { Authorization: `Bearer ${token}` };
  }, [token]);

  const login = useCallback(
    async (email: string, password: string) => {
      setIsLoading(true);
      setError(null);
      try {
        // Adjust payload keys if your backend expects different names
        const formData = new URLSearchParams();
        formData.append("username", email);
        formData.append("password", password);
        const res = await apiFetch("/auth/token", "POST", formData);
        console.log("API response (raw):", res);
        const accessToken = (res && (res.access_token || res.token || res.accessToken)) || null;
        if (!accessToken || typeof accessToken !== "string") {
          throw new Error("Authentication failed: no token returned.");
        }
        setTokenAndStore(accessToken);
      } catch (err: any) {
        setError(err?.message || String(err));
        setTokenAndStore(null);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [setTokenAndStore]
  );

  const register = useCallback(
    async (name: string, email: string, department: string, password: string) => {
      setIsLoading(true);
      setError(null);
      try {
        await apiFetch("/auth/register", "POST", { name, email, department, password });
        await login(email, password);
      } catch (err: any) {
        setError(err?.message || String(err));
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [login]
  );

  const logout = useCallback(() => {
    setTokenAndStore(null);
    setUser(null);
    setError(null);
  }, [setTokenAndStore]);

  const contextValue: AuthContextType = {
    user,
    token,
    isAuthenticated: !!user,
    login,
    logout,
    register,
    isLoading,
    error,
    getAuthHeaders,
  };

  return <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

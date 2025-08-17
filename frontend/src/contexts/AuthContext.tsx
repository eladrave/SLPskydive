import { createContext, useContext, ReactNode } from 'react';
import { apiClient } from '@/api/client';
import { useQuery, useQueryClient } from '@tanstack/react-query';

// Define the shape of the user and the auth context
interface User {
  id: string;
  email: string;
  name: string;
  role: 'mentor' | 'mentee' | 'admin';
}

interface AuthContextType {
  user: User | null;
  login: (data: URLSearchParams) => Promise<any>;
  logout: () => Promise<void>;
  isLoading: boolean;
}

// Create the context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Define the provider component
export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const queryClient = useQueryClient();

  const { data: user, isLoading } = useQuery<User | null>({
    queryKey: ['me'],
    queryFn: async () => {
      try {
        const data = await apiClient.get('/auth/me');
        return data;
      } catch (error) {
        return null;
      }
    },
    retry: false,
    refetchOnWindowFocus: false,
  });

  const login = async (loginData: URLSearchParams) => {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: loginData.toString(),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'An error occurred');
    }

    const data = await response.json();
    await queryClient.invalidateQueries({ queryKey: ['me'] });
    return data;
  };

  const logout = async () => {
    await apiClient.post('/auth/logout', {});
    queryClient.setQueryData(['me'], null);
  };

  const value = {
    user: user || null,
    login,
    logout,
    isLoading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Create a custom hook to use the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

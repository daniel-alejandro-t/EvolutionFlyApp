import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, AuthResponse, LoginCredentials, RegisterData } from '../types';
import { authAPI } from '../services/api';
import { toast } from 'react-toastify';

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (credentials: LoginCredentials) => Promise<boolean>;
  register: (userData: RegisterData) => Promise<boolean>;
  logout: () => void;
  isAuthenticated: boolean;
  isClient: boolean;
  isOperator: boolean;
  isAdmin: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');

    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  const login = async (credentials: LoginCredentials): Promise<boolean> => {
    try {
      const response: AuthResponse = await authAPI.login(credentials);
      
      setUser(response.user);
      setToken(response.token);
      
      localStorage.setItem('token', response.token);
      localStorage.setItem('user', JSON.stringify(response.user));
      
      toast.success(`¡Bienvenido ${response.user.first_name}!`);
      return true;
    } catch (error: any) {
      console.error('Login error:', error);
      toast.error(
        error.response?.data?.non_field_errors?.[0] || 
        error.response?.data?.message || 
        'Error al iniciar sesión'
      );
      return false;
    }
  };

  const register = async (userData: RegisterData): Promise<boolean> => {
    try {
      const response: AuthResponse = await authAPI.register(userData);
      
      setUser(response.user);
      setToken(response.token);
      
      localStorage.setItem('token', response.token);
      localStorage.setItem('user', JSON.stringify(response.user));
      
      toast.success('¡Registro exitoso! Bienvenido a Evolution Fly App');
      return true;
    } catch (error: any) {
      console.error('Register error:', error);
      
      // Handle validation errors
      if (error.response?.data) {
        const errors = error.response.data;
        Object.keys(errors).forEach(key => {
          if (Array.isArray(errors[key])) {
            errors[key].forEach((msg: string) => toast.error(`${key}: ${msg}`));
          } else {
            toast.error(`${key}: ${errors[key]}`);
          }
        });
      } else {
        toast.error('Error al registrar usuario');
      }
      return false;
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setToken(null);
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      toast.info('Sesión cerrada exitosamente');
    }
  };

  const isAuthenticated = Boolean(user && token);
  const isClient = user?.role === 'client';
  const isOperator = user?.role === 'operator';
  const isAdmin = user?.role === 'admin';

  const value: AuthContextType = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    isAuthenticated,
    isClient,
    isOperator,
    isAdmin,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
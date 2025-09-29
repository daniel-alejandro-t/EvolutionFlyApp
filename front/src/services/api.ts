import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (credentials: { email: string; password: string }) => {
    const response = await api.post('/auth/login/', credentials);
    return response.data;
  },
  
  register: async (userData: {
    username: string;
    email: string;
    password: string;
    password_confirm: string;
    first_name: string;
    last_name: string;
    role?: string;
    phone?: string;
  }) => {
    const response = await api.post('/auth/register/', userData);
    return response.data;
  },
  
  logout: async () => {
    await api.post('/auth/logout/');
  },
  
  getProfile: async () => {
    const response = await api.get('/auth/profile/');
    return response.data;
  },
  
  updateProfile: async (userData: any) => {
    const response = await api.put('/auth/profile/', userData);
    return response.data;
  },
};

// Destinations API
export const destinationsAPI = {
  getAll: async () => {
    const response = await api.get('/destinations/destinations/');
    return response.data;
  },
  
  getActive: async () => {
    const response = await api.get('/destinations/destinations/active-destinations/');
    return response.data;
  },
  
  create: async (destinationData: {
    name: string;
    code: string;
    description?: string;
    is_active?: boolean;
  }) => {
    const response = await api.post('/destinations/destinations/', destinationData);
    return response.data;
  },
  
  update: async (id: number, destinationData: any) => {
    const response = await api.put(`/destinations/destinations/${id}/`, destinationData);
    return response.data;
  },
  
  delete: async (id: number) => {
    await api.delete(`/destinations/destinations/${id}/`);
  },
};

// Flight Requests API
export const flightRequestsAPI = {
  getAll: async () => {
    const response = await api.get('/flight-requests/');
    return response.data;
  },
  
  getPending: async () => {
    const response = await api.get('/flight-requests/pending/');
    return response.data;
  },
  
  create: async (requestData: {
    destination: number;
    travel_date: string;
    notes?: string;
  }) => {
    const response = await api.post('/flight-requests/', requestData);
    return response.data;
  },
  
  update: async (id: number, requestData: any) => {
    const response = await api.put(`/flight-requests/${id}/`, requestData);
    return response.data;
  },
  
  reserve: async (id: number, operatorNotes?: string) => {
    const response = await api.post(`/flight-requests/${id}/reserve/`, {
      operator_notes: operatorNotes,
    });
    return response.data;
  },
  
  delete: async (id: number) => {
    await api.delete(`/flight-requests/${id}/`);
  },
};

export default api;
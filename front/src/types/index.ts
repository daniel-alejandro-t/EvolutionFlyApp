export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'client' | 'operator' | 'admin';
  phone?: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}

export interface Destination {
  id: number;
  name: string;
  code: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface FlightRequest {
  id: number;
  user: User;
  destination: Destination;
  travel_date: string;
  status: 'pending' | 'reserved' | 'cancelled' | 'completed';
  status_display: string;
  notes?: string;
  operator_notes?: string;
  reserved_by?: User;
  reserved_at?: string;
  days_until_travel?: number;
  created_at: string;
  updated_at: string;
}

export interface CreateFlightRequest {
  destination: number;
  travel_date: string;
  notes?: string;
}

export interface CreateDestination {
  name: string;
  code: string;
  description?: string;
  is_active?: boolean;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  role?: string;
  phone?: string;
}
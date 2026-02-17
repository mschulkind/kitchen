/**
 * API Client for Kitchen Backend 🧠
 * 
 * Wrapper for the FastAPI "Chef's Brain" service.
 * Used for AI-powered features (planning, vision, parsing).
 */

import { Platform } from 'react-native';

const isAndroidEmulator = () => {
  if (Platform.OS !== 'android') return false;
  try {
    const constants = (require('react-native') as any).Platform?.constants;
    return constants?.androidID === 'generic' || constants?.manufacturer === 'unknown';
  } catch {
    return false;
  }
};

const getApiUrl = () => {
  // Explicit override from env (takes precedence)
  if (process.env.EXPO_PUBLIC_API_URL) {
    return process.env.EXPO_PUBLIC_API_URL;
  }

  // Web/Browser: Use localhost
  if (Platform.OS === 'web') {
    return 'http://localhost:5300';
  }

  // Android Emulator: Map 192.168.1.2 -> 10.0.2.2
  if (isAndroidEmulator()) {
    return 'http://10.0.2.2:5300';
  }

  // Physical device or iOS: Use NAS IP
  return 'http://192.168.1.2:5300';
};

const API_URL = getApiUrl();

/**
 * Base fetch wrapper with error handling
 */
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_URL}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }

  return response.json();
}

/**
 * Pantry API endpoints
 */
export const pantryApi = {
  list: (params?: { page?: number; per_page?: number }) => 
    apiFetch<PantryItemList>(`/api/v1/pantry?${new URLSearchParams(params as any)}`),
  
  get: (id: string) => 
    apiFetch<PantryItem>(`/api/v1/pantry/${id}`),
  
  create: (data: CreatePantryItem) => 
    apiFetch<PantryItem>('/api/v1/pantry', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  update: (id: string, data: UpdatePantryItem) => 
    apiFetch<PantryItem>(`/api/v1/pantry/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  
  delete: (id: string) => 
    apiFetch<void>(`/api/v1/pantry/${id}`, { method: 'DELETE' }),
  
  search: (q: string) => 
    apiFetch<PantryItem[]>(`/api/v1/pantry/search?q=${encodeURIComponent(q)}`),
  
  // Lazy Discovery (D13)
  confirmPossession: (itemName: string, unit = 'count', quantity = 1) =>
    apiFetch<PantryItem>(`/api/v1/pantry/confirm?item_name=${encodeURIComponent(itemName)}&unit=${unit}&quantity=${quantity}`, {
      method: 'POST',
    }),
};

/**
 * Health check
 */
export const healthApi = {
  check: () => apiFetch<{ status: string }>('/health'),
};

// Types
export interface PantryItem {
  id: string;
  household_id: string;
  name: string;
  quantity: number;
  unit: string;
  location: 'pantry' | 'fridge' | 'freezer' | 'counter' | 'garden';
  expiry_date: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface PantryItemList {
  items: PantryItem[];
  total: number;
  page: number;
  per_page: number;
}

export interface CreatePantryItem {
  name: string;
  quantity: number;
  unit: string;
  location?: 'pantry' | 'fridge' | 'freezer' | 'counter' | 'garden';
  expiry_date?: string;
  notes?: string;
}

export interface UpdatePantryItem {
  name?: string;
  quantity?: number;
  unit?: string;
  location?: 'pantry' | 'fridge' | 'freezer' | 'counter' | 'garden';
  expiry_date?: string;
  notes?: string;
}

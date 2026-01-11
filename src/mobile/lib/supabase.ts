/**
 * Supabase Client Configuration 🔌
 * 
 * Connects to self-hosted Supabase instance (Decision D4).
 * Handles auth state persistence and realtime subscriptions.
 */

import { createClient } from '@supabase/supabase-js';
import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';

// Environment configuration
// In production, these come from app.json extra or environment
const SUPABASE_URL = process.env.EXPO_PUBLIC_SUPABASE_URL || 'http://localhost:8001';
const SUPABASE_ANON_KEY = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY || 'test-key-for-development';

// Flag to indicate if we're running in development mode without real Supabase
export const IS_MOCK_SUPABASE = !process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY;

/**
 * Secure storage adapter for auth tokens.
 * Uses SecureStore on native, localStorage on web.
 */
const secureStorage = {
  getItem: async (key: string): Promise<string | null> => {
    if (Platform.OS === 'web') {
      return localStorage.getItem(key);
    }
    return SecureStore.getItemAsync(key);
  },
  setItem: async (key: string, value: string): Promise<void> => {
    if (Platform.OS === 'web') {
      localStorage.setItem(key, value);
      return;
    }
    await SecureStore.setItemAsync(key, value);
  },
  removeItem: async (key: string): Promise<void> => {
    if (Platform.OS === 'web') {
      localStorage.removeItem(key);
      return;
    }
    await SecureStore.deleteItemAsync(key);
  },
};

/**
 * Supabase client instance.
 * 
 * Usage:
 * ```ts
 * import { supabase } from '@/lib/supabase';
 * const { data } = await supabase.from('pantry_items').select('*');
 * ```
 */
export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: {
    storage: secureStorage,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false,
  },
  realtime: {
    params: {
      eventsPerSecond: 10,
    },
  },
});

/**
 * Database table types (will be auto-generated later with Supabase CLI)
 */
export type Database = {
  public: {
    Tables: {
      pantry_items: {
        Row: {
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
        };
        Insert: Omit<Database['public']['Tables']['pantry_items']['Row'], 'id' | 'created_at' | 'updated_at'>;
        Update: Partial<Database['public']['Tables']['pantry_items']['Insert']>;
      };
      households: {
        Row: {
          id: string;
          name: string;
          owner_id: string;
          created_at: string;
          updated_at: string;
        };
      };
    };
  };
};

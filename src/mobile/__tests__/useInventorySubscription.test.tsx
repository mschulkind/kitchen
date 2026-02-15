/**
 * Tests for useInventorySubscription Hook 🧪
 * 
 * Tests the realtime subscription behavior for inventory updates.
 */

import { renderHook, act, waitFor } from '@testing-library/react-native';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

// Mock supabase client
const mockSubscribe = jest.fn();
const mockOn = jest.fn().mockReturnValue({ subscribe: mockSubscribe });
const mockChannel = jest.fn().mockReturnValue({ on: mockOn });
const mockRemoveChannel = jest.fn();
const mockGetUser = jest.fn().mockResolvedValue({ data: { user: null }, error: null });
const mockSingle = jest.fn().mockResolvedValue({ data: null, error: { code: 'PGRST116', message: 'No rows' } });
const mockLimit = jest.fn().mockReturnValue({ single: mockSingle });
const mockEq = jest.fn().mockReturnValue({ limit: mockLimit });
const mockSelect = jest.fn().mockReturnValue({ eq: mockEq });
const mockFrom = jest.fn().mockReturnValue({ select: mockSelect });

jest.mock('../lib/supabase', () => {
  return {
    supabase: {
      channel: (...args: any[]) => mockChannel(...args),
      removeChannel: (...args: any[]) => mockRemoveChannel(...args),
      auth: {
        getUser: (...args: any[]) => mockGetUser(...args),
      },
      from: (...args: any[]) => mockFrom(...args),
    },
    Database: {},
  };
});

import { useInventorySubscription, useHouseholdId } from '../hooks/useInventorySubscription';

// Create a wrapper with QueryClient
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('useInventorySubscription', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockSubscribe.mockImplementation((callback) => {
      callback('SUBSCRIBED');
      return { unsubscribe: jest.fn() };
    });
  });

  describe('Subscription Setup', () => {
    it('creates a channel with correct name when enabled', () => {
      const householdId = 'test-household-123';
      
      renderHook(() => useInventorySubscription(householdId), {
        wrapper: createWrapper(),
      });

      expect(mockChannel).toHaveBeenCalledWith(`pantry:${householdId}`);
    });

    it('subscribes to postgres_changes on pantry_items table', () => {
      const householdId = 'test-household-123';
      
      renderHook(() => useInventorySubscription(householdId), {
        wrapper: createWrapper(),
      });

      expect(mockOn).toHaveBeenCalledWith(
        'postgres_changes',
        expect.objectContaining({
          event: '*',
          schema: 'public',
          table: 'pantry_items',
          filter: `household_id=eq.${householdId}`,
        }),
        expect.any(Function)
      );
    });

    it('does not create subscription when householdId is null', () => {
      renderHook(() => useInventorySubscription(null), {
        wrapper: createWrapper(),
      });

      expect(mockChannel).not.toHaveBeenCalled();
    });

    it('does not create subscription when disabled', () => {
      renderHook(() => useInventorySubscription('household-123', false), {
        wrapper: createWrapper(),
      });

      expect(mockChannel).not.toHaveBeenCalled();
    });
  });

  describe('Subscription Cleanup', () => {
    it('removes channel on unmount', () => {
      const { unmount } = renderHook(
        () => useInventorySubscription('test-household'),
        { wrapper: createWrapper() }
      );

      unmount();

      expect(mockRemoveChannel).toHaveBeenCalled();
    });

    it('removes old channel when householdId changes', () => {
      const { rerender } = renderHook(
        ({ householdId }: { householdId: string | null }) => useInventorySubscription(householdId),
        { 
          wrapper: createWrapper(),
          initialProps: { householdId: 'household-1' }
        }
      );

      // Change household
      rerender({ householdId: 'household-2' });

      // Should have removed old channel and created new
      expect(mockRemoveChannel).toHaveBeenCalled();
      expect(mockChannel).toHaveBeenCalledWith('pantry:household-2');
    });
  });

  describe('Query Invalidation', () => {
    it('invalidates pantry queries on INSERT event', async () => {
      const queryClient = new QueryClient();
      const invalidateSpy = jest.spyOn(queryClient, 'invalidateQueries');
      
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      );

      // Capture the callback passed to .on()
      let changeCallback: Function;
      (mockOn as jest.Mock).mockImplementation((event: any, config: any, callback: any) => {
        changeCallback = callback;
        return { subscribe: mockSubscribe };
      });

      renderHook(() => useInventorySubscription('test-household'), { wrapper });

      // Simulate an INSERT event
      act(() => {
        changeCallback!({
          eventType: 'INSERT',
          new: { id: 'new-item', name: 'Test Item' },
          old: {},
        });
      });

      expect(invalidateSpy).toHaveBeenCalledWith({
        queryKey: ['pantry', 'test-household'],
      });
    });

    it('invalidates pantry queries on UPDATE event', async () => {
      const queryClient = new QueryClient();
      const invalidateSpy = jest.spyOn(queryClient, 'invalidateQueries');
      
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      );

      let changeCallback: Function;
      (mockOn as jest.Mock).mockImplementation((event: any, config: any, callback: any) => {
        changeCallback = callback;
        return { subscribe: mockSubscribe };
      });

      renderHook(() => useInventorySubscription('test-household'), { wrapper });

      act(() => {
        changeCallback!({
          eventType: 'UPDATE',
          new: { id: 'item-1', quantity: 5 },
          old: { id: 'item-1', quantity: 3 },
        });
      });

      expect(invalidateSpy).toHaveBeenCalled();
    });

    it('invalidates pantry queries on DELETE event', async () => {
      const queryClient = new QueryClient();
      const invalidateSpy = jest.spyOn(queryClient, 'invalidateQueries');
      
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      );

      let changeCallback: Function;
      (mockOn as jest.Mock).mockImplementation((event: any, config: any, callback: any) => {
        changeCallback = callback;
        return { subscribe: mockSubscribe };
      });

      renderHook(() => useInventorySubscription('test-household'), { wrapper });

      act(() => {
        changeCallback!({
          eventType: 'DELETE',
          new: {},
          old: { id: 'deleted-item' },
        });
      });

      expect(invalidateSpy).toHaveBeenCalled();
    });
  });
});

describe('useHouseholdId', () => {
  it('returns null when no user is authenticated', async () => {
    mockGetUser.mockResolvedValueOnce({ data: { user: null }, error: null });
    
    const { result } = renderHook(() => useHouseholdId());

    // Initially null while fetching
    expect(result.current).toBeNull();
    
    // After async resolution, still null (no user)
    await waitFor(() => {
      expect(result.current).toBeNull();
    });
  });

  it('returns household ID when user is authenticated', async () => {
    mockGetUser.mockResolvedValueOnce({ data: { user: { id: 'user-123' } }, error: null });
    mockSingle.mockResolvedValueOnce({ data: { household_id: 'hh-456' }, error: null });

    const { result } = renderHook(() => useHouseholdId());

    await waitFor(() => {
      expect(result.current).toBe('hh-456');
    });
  });
});

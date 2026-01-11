/**
 * useInventorySubscription Hook 📡
 * 
 * Realtime subscription to pantry_items table changes.
 * Implements the core requirement from central-plan.md:
 * "Updates made by User A must reflect instantly on User B's device."
 * 
 * Fun fact: Supabase Realtime uses PostgreSQL's NOTIFY/LISTEN under the hood! 🐘
 */

import { useEffect, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { RealtimeChannel, RealtimePostgresChangesPayload } from '@supabase/supabase-js';
import { supabase, Database } from '@/lib/supabase';

type PantryItem = Database['public']['Tables']['pantry_items']['Row'];
type PantryPayload = RealtimePostgresChangesPayload<PantryItem>;

/**
 * Subscribe to realtime changes on the pantry_items table.
 * Automatically invalidates TanStack Query cache on changes.
 * 
 * @param householdId - The household to subscribe to
 * @param enabled - Whether the subscription is active
 * 
 * @example
 * ```tsx
 * function InventoryScreen() {
 *   useInventorySubscription(householdId);
 *   const { data } = useQuery(['pantry', householdId], fetchPantryItems);
 *   // Data automatically updates when other users make changes!
 * }
 * ```
 */
export function useInventorySubscription(
  householdId: string | null,
  enabled = true
) {
  const queryClient = useQueryClient();

  const handleChange = useCallback(
    (payload: PantryPayload) => {
      console.log('🔔 Realtime update:', payload.eventType, payload);

      // Invalidate the pantry query to refetch
      queryClient.invalidateQueries({ queryKey: ['pantry', householdId] });

      // For optimistic updates, we could also directly update the cache:
      // queryClient.setQueryData(['pantry', householdId], (old) => ...)
    },
    [queryClient, householdId]
  );

  useEffect(() => {
    if (!enabled || !householdId) return;

    let channel: RealtimeChannel;

    const setupSubscription = async () => {
      channel = supabase
        .channel(`pantry:${householdId}`)
        .on<PantryItem>(
          'postgres_changes',
          {
            event: '*', // INSERT, UPDATE, DELETE
            schema: 'public',
            table: 'pantry_items',
            filter: `household_id=eq.${householdId}`,
          },
          handleChange
        )
        .subscribe((status) => {
          console.log('📡 Subscription status:', status);
        });
    };

    setupSubscription();

    // Cleanup on unmount or householdId change
    return () => {
      if (channel) {
        console.log('🔌 Unsubscribing from realtime channel');
        supabase.removeChannel(channel);
      }
    };
  }, [householdId, enabled, handleChange]);
}

/**
 * Hook to get the current user's household ID.
 * In production, this would come from the auth context.
 */
export function useHouseholdId(): string | null {
  // TODO: Replace with actual auth integration
  // For now, return the development household
  return '00000000-0000-0000-0000-000000000001';
}

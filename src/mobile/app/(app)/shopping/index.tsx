/**
 * Shopping List Screen 🛒
 * 
 * Grouped shopping list with check/uncheck, swipe to delete.
 * Realtime sync for multi-user shopping.
 * Per frontend-redesign.md Section 2.6
 * 
 * Fun fact: The average grocery list has 15-20 items! 📝
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { FlatList, RefreshControl, Pressable, Animated } from 'react-native';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Stack } from 'expo-router';
import {
  YStack,
  XStack,
  H2,
  H3,
  Text,
  Paragraph,
  Button,
  Input,
  Card,
  Spinner,
  Checkbox,
} from 'tamagui';
import {
  Plus,
  Trash2,
  Check,
  ShoppingCart,
  Mic,
} from '@tamagui/lucide-icons';

import { supabase } from '@/lib/supabase';
import { useHouseholdId } from '@/hooks/useInventorySubscription';
import { KitchenButton, KitchenInput } from '@/components';

type ShoppingItem = {
  id: string;
  name: string;
  quantity?: string;
  unit?: string;
  category?: string;
  checked: boolean;
  created_at: string;
};

type GroupedItems = {
  category: string;
  items: ShoppingItem[];
};

// Category order for smart sorting
const CATEGORY_ORDER = [
  'Produce',
  'Dairy',
  'Meat & Seafood',
  'Bakery',
  'Frozen',
  'Pantry',
  'Beverages',
  'Other',
];

export default function ShoppingScreen() {
  const householdId = useHouseholdId();
  const queryClient = useQueryClient();
  
  const [newItemName, setNewItemName] = useState('');
  const [showCompleted, setShowCompleted] = useState(true);

  // Fetch shopping list with realtime subscription
  const { data: items, isLoading, refetch, isRefetching } = useQuery({
    queryKey: ['shopping_list', householdId],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('shopping_list')
        .select('*')
        .order('checked')
        .order('category')
        .order('name');

      if (error) throw error;
      return data as ShoppingItem[];
    },
  });

  // Realtime subscription
  useEffect(() => {
    const channel = supabase
      .channel('shopping_list_changes')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'shopping_list',
        },
        () => {
          queryClient.invalidateQueries({ queryKey: ['shopping_list'] });
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [queryClient]);

  // Add item mutation
  const addItem = useMutation({
    mutationFn: async (name: string) => {
      const { error } = await supabase.from('shopping_list').insert({
        name: name.trim(),
        category: 'Other',
        checked: false,
      });
      if (error) throw error;
    },
    onSuccess: () => {
      setNewItemName('');
      queryClient.invalidateQueries({ queryKey: ['shopping_list'] });
    },
  });

  // Toggle checked mutation
  const toggleChecked = useMutation({
    mutationFn: async ({ id, checked }: { id: string; checked: boolean }) => {
      const { error } = await supabase
        .from('shopping_list')
        .update({ checked: !checked })
        .eq('id', id);
      if (error) throw error;
    },
    onMutate: async ({ id, checked }) => {
      // Optimistic update
      await queryClient.cancelQueries({ queryKey: ['shopping_list'] });
      const previous = queryClient.getQueryData(['shopping_list', householdId]);
      queryClient.setQueryData(
        ['shopping_list', householdId],
        (old: ShoppingItem[] | undefined) =>
          old?.map((item) =>
            item.id === id ? { ...item, checked: !checked } : item
          )
      );
      return { previous };
    },
    onError: (err, variables, context) => {
      queryClient.setQueryData(['shopping_list', householdId], context?.previous);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['shopping_list'] });
    },
  });

  // Delete item mutation
  const deleteItem = useMutation({
    mutationFn: async (id: string) => {
      const { error } = await supabase
        .from('shopping_list')
        .delete()
        .eq('id', id);
      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shopping_list'] });
    },
  });

  // Clear completed mutation
  const clearCompleted = useMutation({
    mutationFn: async () => {
      const { error } = await supabase
        .from('shopping_list')
        .delete()
        .eq('checked', true);
      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shopping_list'] });
    },
  });

  // Handle add item
  const handleAddItem = useCallback(() => {
    if (newItemName.trim()) {
      addItem.mutate(newItemName);
    }
  }, [newItemName, addItem]);

  // Group items by category
  const groupedItems = useMemo(() => {
    if (!items) return [];

    const unchecked = items.filter((i) => !i.checked);
    const checked = items.filter((i) => i.checked);

    // Group unchecked by category
    const groups: Record<string, ShoppingItem[]> = {};
    unchecked.forEach((item) => {
      const cat = item.category || 'Other';
      if (!groups[cat]) groups[cat] = [];
      groups[cat].push(item);
    });

    // Sort by category order
    const sortedGroups: GroupedItems[] = CATEGORY_ORDER
      .filter((cat) => groups[cat])
      .map((cat) => ({ category: cat, items: groups[cat] }));

    // Add any categories not in the order
    Object.keys(groups)
      .filter((cat) => !CATEGORY_ORDER.includes(cat))
      .forEach((cat) => {
        sortedGroups.push({ category: cat, items: groups[cat] });
      });

    // Add completed section
    if (checked.length > 0 && showCompleted) {
      sortedGroups.push({ category: 'Completed', items: checked });
    }

    return sortedGroups;
  }, [items, showCompleted]);

  const uncheckedCount = items?.filter((i) => !i.checked).length || 0;
  const checkedCount = items?.filter((i) => i.checked).length || 0;

  return (
    <>
      <Stack.Screen
        options={{
          headerRight: () =>
            checkedCount > 0 ? (
              <Button
                testID="clear-completed-button"
                size="$3"
                chromeless
                color="$red10"
                onPress={() => clearCompleted.mutate()}
              >
                Clear Completed
              </Button>
            ) : null,
        }}
      />

      <YStack flex={1} backgroundColor="$background">
        {/* Add Item Input */}
        <XStack padding="$4" space="$2" borderBottomWidth={1} borderBottomColor="$gray4">
          <Input
            testID="add-item-input"
            flex={1}
            placeholder="Add item..."
            value={newItemName}
            onChangeText={setNewItemName}
            onSubmitEditing={handleAddItem}
            returnKeyType="done"
          />
          <Button
            testID="add-item-button"
            size="$4"
            theme="orange"
            icon={<Plus size={20} />}
            onPress={handleAddItem}
            disabled={!newItemName.trim() || addItem.isPending}
          />
          <Button
            testID="voice-add-button"
            size="$4"
            theme="gray"
            icon={<Mic size={20} />}
            onPress={() => {
              // TODO: Implement voice input in Phase 9
              console.log('Voice input placeholder');
            }}
          />
        </XStack>

        {/* List */}
        {isLoading ? (
          <YStack flex={1} justifyContent="center" alignItems="center">
            <Spinner size="large" color="$orange10" />
          </YStack>
        ) : items?.length === 0 ? (
          <YStack flex={1} justifyContent="center" alignItems="center" padding="$6" testID="shopping-empty-state">
            <ShoppingCart size={60} color="$gray8" />
            <H3 marginTop="$4" color="$gray11">
              Your list is empty
            </H3>
            <Paragraph color="$gray10" textAlign="center">
              Add items above or generate from your meal plan.
            </Paragraph>
          </YStack>
        ) : (
          <FlatList
            data={groupedItems}
            keyExtractor={(group) => group.category}
            refreshControl={
              <RefreshControl refreshing={isRefetching} onRefresh={refetch} />
            }
            contentContainerStyle={{ padding: 16, paddingBottom: 40 }}
            renderItem={({ item: group }) => (
              <YStack marginBottom="$4" testID={`category-${group.category}`}>
                <XStack justifyContent="space-between" alignItems="center" marginBottom="$2">
                  <H3
                    color={group.category === 'Completed' ? '$gray10' : '$gray12'}
                    fontSize="$4"
                  >
                    {group.category}
                  </H3>
                  <Text color="$gray10" fontSize="$2">
                    {group.items.length}
                  </Text>
                </XStack>

                <Card bordered testID={group.category === 'Completed' ? 'completed-items' : undefined}>
                  {group.items.map((item, idx) => (
                    <XStack
                      key={item.id}
                      padding="$3"
                      borderBottomWidth={idx < group.items.length - 1 ? 1 : 0}
                      borderBottomColor="$gray4"
                      alignItems="center"
                      opacity={item.checked ? 0.5 : 1}
                      testID={`shopping-item-${item.id}`}
                    >
                      <Checkbox
                        testID={`check-${item.name}`}
                        size="$5"
                        checked={item.checked}
                        onCheckedChange={() =>
                          toggleChecked.mutate({ id: item.id, checked: item.checked })
                        }
                      >
                        <Checkbox.Indicator>
                          <Check size={16} />
                        </Checkbox.Indicator>
                      </Checkbox>

                      <YStack flex={1} marginLeft="$3">
                        <Text
                          color="$gray12"
                          textDecorationLine={item.checked ? 'line-through' : 'none'}
                        >
                          {item.name}
                        </Text>
                        {item.quantity && (
                          <Text fontSize="$2" color="$gray10">
                            {item.quantity} {item.unit}
                          </Text>
                        )}
                      </YStack>

                      <Button
                        testID={`delete-${item.id}`}
                        size="$2"
                        circular
                        chromeless
                        icon={<Trash2 size={16} color="$red10" />}
                        onPress={() => deleteItem.mutate(item.id)}
                      />
                    </XStack>
                  ))}
                </Card>
              </YStack>
            )}
          />
        )}

        {/* Summary Footer */}
        {items && items.length > 0 && (
          <XStack
            testID="shopping-summary"
            padding="$4"
            borderTopWidth={1}
            borderTopColor="$gray4"
            justifyContent="space-between"
            backgroundColor="$background"
          >
            <Text color="$gray10">
              {uncheckedCount} item{uncheckedCount !== 1 ? 's' : ''} to buy
            </Text>
            {checkedCount > 0 && (
              <Text color="$green10">
                ✓ {checkedCount} completed
              </Text>
            )}
          </XStack>
        )}
      </YStack>
    </>
  );
}

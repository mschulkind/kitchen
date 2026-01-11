/**
 * Inventory List Screen 📦
 * 
 * Main pantry view with realtime sync.
 * Phase 1C core deliverable.
 */

import { useState } from 'react';
import { FlatList, RefreshControl } from 'react-native';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link, Stack } from 'expo-router';
import {
  YStack,
  XStack,
  Text,
  Button,
  Input,
  Spinner,
  Sheet,
} from 'tamagui';
import { Plus, Search, Package } from '@tamagui/lucide-icons';

import { supabase, Database } from '@/lib/supabase';
import { useInventorySubscription, useHouseholdId } from '@/hooks/useInventorySubscription';
import { PantryItemCard } from '@/components/PantryItemCard';

type PantryItem = Database['public']['Tables']['pantry_items']['Row'];

export default function InventoryScreen() {
  const householdId = useHouseholdId();
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState('');
  const [isAddSheetOpen, setIsAddSheetOpen] = useState(false);

  // Enable realtime subscription 📡
  useInventorySubscription(householdId);

  // Fetch pantry items
  const { data: items, isLoading, refetch, isRefetching } = useQuery({
    queryKey: ['pantry', householdId],
    queryFn: async () => {
      if (!householdId) return [];
      
      const { data, error } = await supabase
        .from('pantry_items')
        .select('*')
        .eq('household_id', householdId)
        .order('name');

      if (error) throw error;
      return data as PantryItem[];
    },
    enabled: !!householdId,
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      const { error } = await supabase
        .from('pantry_items')
        .delete()
        .eq('id', id);
      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pantry', householdId] });
    },
  });

  // Filter items by search
  const filteredItems = items?.filter((item) =>
    item.name.toLowerCase().includes(searchQuery.toLowerCase())
  ) ?? [];

  // Group by location
  const groupedItems = filteredItems.reduce((acc, item) => {
    const location = item.location || 'pantry';
    if (!acc[location]) acc[location] = [];
    acc[location].push(item);
    return acc;
  }, {} as Record<string, PantryItem[]>);

  const locationOrder = ['fridge', 'freezer', 'pantry', 'counter', 'garden'];
  const sortedLocations = Object.keys(groupedItems).sort(
    (a, b) => locationOrder.indexOf(a) - locationOrder.indexOf(b)
  );

  return (
    <>
      <Stack.Screen
        options={{
          title: 'Pantry',
          headerRight: () => (
            <Button
              size="$3"
              circular
              icon={<Plus size={20} />}
              onPress={() => setIsAddSheetOpen(true)}
              marginRight="$2"
            />
          ),
        }}
      />

      <YStack flex={1} backgroundColor="$background">
        {/* Search Bar */}
        <XStack padding="$3" space="$2">
          <Input
            flex={1}
            size="$4"
            placeholder="Search items..."
            value={searchQuery}
            onChangeText={setSearchQuery}
            borderRadius="$4"
          />
          <Button size="$4" icon={<Search size={20} />} />
        </XStack>

        {/* Item List */}
        {isLoading ? (
          <YStack flex={1} justifyContent="center" alignItems="center">
            <Spinner size="large" color="$blue10" />
            <Text marginTop="$3" color="$gray10">Loading pantry...</Text>
          </YStack>
        ) : filteredItems.length === 0 ? (
          <YStack flex={1} justifyContent="center" alignItems="center" padding="$6">
            <Package size={64} color="#ccc" />
            <Text fontSize="$6" marginTop="$4" textAlign="center">
              Your pantry is empty
            </Text>
            <Text color="$gray10" textAlign="center" marginTop="$2">
              Tap the + button to add items
            </Text>
            <Button
              size="$5"
              theme="blue"
              marginTop="$4"
              icon={<Plus size={20} />}
              onPress={() => setIsAddSheetOpen(true)}
            >
              Add First Item
            </Button>
          </YStack>
        ) : (
          <FlatList
            data={sortedLocations}
            keyExtractor={(location) => location}
            refreshControl={
              <RefreshControl refreshing={isRefetching} onRefresh={refetch} />
            }
            renderItem={({ item: location }) => (
              <YStack padding="$3">
                <Text
                  fontSize="$5"
                  fontWeight="bold"
                  textTransform="capitalize"
                  marginBottom="$2"
                  color="$gray11"
                >
                  {location === 'garden' ? '🌱 Garden' :
                   location === 'fridge' ? '❄️ Fridge' :
                   location === 'freezer' ? '🧊 Freezer' :
                   location === 'counter' ? '🍌 Counter' :
                   '🥫 Pantry'}
                </Text>
                {groupedItems[location].map((item) => (
                  <PantryItemCard
                    key={item.id}
                    item={item}
                    onDelete={() => deleteMutation.mutate(item.id)}
                  />
                ))}
              </YStack>
            )}
          />
        )}
      </YStack>

      {/* Add Item Sheet */}
      <AddItemSheet
        open={isAddSheetOpen}
        onOpenChange={setIsAddSheetOpen}
        householdId={householdId}
      />
    </>
  );
}

// Add Item Sheet Component
function AddItemSheet({
  open,
  onOpenChange,
  householdId,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  householdId: string | null;
}) {
  const queryClient = useQueryClient();
  const [name, setName] = useState('');
  const [quantity, setQuantity] = useState('1');
  const [unit, setUnit] = useState('count');
  const [location, setLocation] = useState<PantryItem['location']>('pantry');

  const createMutation = useMutation({
    mutationFn: async () => {
      if (!householdId) throw new Error('No household');
      
      const { error } = await supabase.from('pantry_items').insert({
        household_id: householdId,
        name,
        quantity: parseFloat(quantity) || 1,
        unit,
        location,
      });
      
      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pantry', householdId] });
      onOpenChange(false);
      // Reset form
      setName('');
      setQuantity('1');
      setUnit('count');
      setLocation('pantry');
    },
  });

  return (
    <Sheet
      open={open}
      onOpenChange={onOpenChange}
      snapPoints={[50]}
      dismissOnSnapToBottom
    >
      <Sheet.Overlay />
      <Sheet.Frame padding="$4">
        <Sheet.Handle />
        <YStack space="$4" marginTop="$4">
          <Text fontSize="$7" fontWeight="bold">Add Item ➕</Text>
          
          <Input
            size="$4"
            placeholder="Item name (e.g., Milk)"
            value={name}
            onChangeText={setName}
            autoFocus
          />
          
          <XStack space="$3">
            <Input
              flex={1}
              size="$4"
              placeholder="Qty"
              keyboardType="numeric"
              value={quantity}
              onChangeText={setQuantity}
            />
            <Input
              flex={2}
              size="$4"
              placeholder="Unit (kg, count, ml)"
              value={unit}
              onChangeText={setUnit}
            />
          </XStack>

          <XStack space="$2" flexWrap="wrap">
            {(['pantry', 'fridge', 'freezer', 'counter', 'garden'] as const).map((loc) => (
              <Button
                key={loc}
                size="$3"
                theme={location === loc ? 'blue' : 'gray'}
                onPress={() => setLocation(loc)}
              >
                {loc === 'garden' ? '🌱' :
                 loc === 'fridge' ? '❄️' :
                 loc === 'freezer' ? '🧊' :
                 loc === 'counter' ? '🍌' : '🥫'} {loc}
              </Button>
            ))}
          </XStack>

          <Button
            size="$5"
            theme="green"
            disabled={!name.trim() || createMutation.isPending}
            onPress={() => createMutation.mutate()}
          >
            {createMutation.isPending ? <Spinner /> : 'Save'}
          </Button>
        </YStack>
      </Sheet.Frame>
    </Sheet>
  );
}

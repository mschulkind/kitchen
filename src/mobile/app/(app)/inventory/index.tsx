/**
 * Inventory List Screen 📦
 * 
 * Main pantry view with filter/sort, realtime sync.
 * Enhanced per frontend-redesign.md Section 2.5
 * 
 * Fun fact: The average household has about 500 items in their kitchen! 📊
 */

import { useState, useMemo } from 'react';
import { FlatList, RefreshControl } from 'react-native';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter, Stack } from 'expo-router';
import {
  YStack,
  XStack,
  Text,
  Button,
  Input,
  Spinner,
  Sheet,
  Select,
} from 'tamagui';
import {
  Plus,
  Search,
  Package,
  Camera,
  SortAsc,
  Filter,
  ChevronDown,
} from '@tamagui/lucide-icons';

import { supabase, Database } from '@/lib/supabase';
import { useInventorySubscription, useHouseholdId } from '@/hooks/useInventorySubscription';
import { PantryItemCard } from '@/components/PantryItemCard';
import { FAB } from '@/components/Core/Button';

type PantryItem = Database['public']['Tables']['pantry_items']['Row'];

type SortOption = 'name' | 'expiry' | 'quantity' | 'location';
type FilterLocation = 'all' | 'fridge' | 'freezer' | 'pantry' | 'counter' | 'garden';

export default function InventoryScreen() {
  const router = useRouter();
  const householdId = useHouseholdId();
  const queryClient = useQueryClient();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<SortOption>('name');
  const [filterLocation, setFilterLocation] = useState<FilterLocation>('all');
  const [isAddSheetOpen, setIsAddSheetOpen] = useState(false);
  const [showActionSheet, setShowActionSheet] = useState(false);

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

  // Filter and sort items
  const processedItems = useMemo(() => {
    if (!items) return [];

    let filtered = items.filter((item) =>
      item.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    // Apply location filter
    if (filterLocation !== 'all') {
      filtered = filtered.filter((item) => item.location === filterLocation);
    }

    // Apply sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'expiry':
          if (!a.expires_at && !b.expires_at) return 0;
          if (!a.expires_at) return 1;
          if (!b.expires_at) return -1;
          return new Date(a.expires_at).getTime() - new Date(b.expires_at).getTime();
        case 'quantity':
          return (a.quantity || 0) - (b.quantity || 0);
        case 'location':
          return (a.location || '').localeCompare(b.location || '');
        default:
          return a.name.localeCompare(b.name);
      }
    });

    return filtered;
  }, [items, searchQuery, sortBy, filterLocation]);

  // Group by location for display
  const groupedItems = useMemo(() => {
    return processedItems.reduce((acc, item) => {
      const location = item.location || 'pantry';
      if (!acc[location]) acc[location] = [];
      acc[location].push(item);
      return acc;
    }, {} as Record<string, PantryItem[]>);
  }, [processedItems]);

  const locationOrder = ['fridge', 'freezer', 'pantry', 'counter', 'garden'];
  const sortedLocations = Object.keys(groupedItems).sort(
    (a, b) => locationOrder.indexOf(a) - locationOrder.indexOf(b)
  );

  // Expiring items count
  const expiringCount = useMemo(() => {
    if (!items) return 0;
    const soon = new Date();
    soon.setDate(soon.getDate() + 3);
    return items.filter(
      (i) => i.expires_at && new Date(i.expires_at) <= soon
    ).length;
  }, [items]);

  const getLocationEmoji = (loc: string) => {
    switch (loc) {
      case 'garden': return '🌱';
      case 'fridge': return '❄️';
      case 'freezer': return '🧊';
      case 'counter': return '🍌';
      default: return '🥫';
    }
  };

  return (
    <>
      <Stack.Screen
        options={{
          title: 'Pantry',
          headerRight: () => (
            <Button
              testID="add-item-button"
              size="$3"
              circular
              icon={<Plus size={20} />}
              onPress={() => setShowActionSheet(true)}
              marginRight="$2"
            />
          ),
        }}
      />

      <YStack flex={1} backgroundColor="$background">
        {/* Search & Filter Bar */}
        <YStack padding="$3" borderBottomWidth={1} borderBottomColor="$gray4">
          <XStack space="$2" marginBottom="$2">
            <XStack flex={1} alignItems="center" space="$2">
              <Search size={18} color="$gray10" />
              <Input
                testID="search-input"
                flex={1}
                size="$4"
                placeholder="Search items..."
                value={searchQuery}
                onChangeText={setSearchQuery}
                borderWidth={0}
                backgroundColor="transparent"
              />
            </XStack>
          </XStack>

          <XStack space="$2">
            {/* Sort Selector */}
            <Select
              value={sortBy}
              onValueChange={(v) => setSortBy(v as SortOption)}
              disablePreventBodyScroll
            >
              <Select.Trigger
                testID="sort-select"
                flex={1}
                size="$3"
                iconAfter={ChevronDown}
              >
                <Select.Value placeholder="Sort by" />
              </Select.Trigger>

              <Select.Content zIndex={200000}>
                <Select.Viewport>
                  <Select.Item index={0} value="name">
                    <Select.ItemText>Name</Select.ItemText>
                  </Select.Item>
                  <Select.Item index={1} value="expiry">
                    <Select.ItemText>Expiry Date</Select.ItemText>
                  </Select.Item>
                  <Select.Item index={2} value="quantity">
                    <Select.ItemText>Quantity</Select.ItemText>
                  </Select.Item>
                  <Select.Item index={3} value="location">
                    <Select.ItemText>Location</Select.ItemText>
                  </Select.Item>
                </Select.Viewport>
              </Select.Content>
            </Select>

            {/* Location Filter */}
            <Select
              value={filterLocation}
              onValueChange={(v) => setFilterLocation(v as FilterLocation)}
              disablePreventBodyScroll
            >
              <Select.Trigger
                testID="filter-select"
                flex={1}
                size="$3"
                iconAfter={ChevronDown}
              >
                <Select.Value placeholder="Filter" />
              </Select.Trigger>

              <Select.Content zIndex={200000}>
                <Select.Viewport>
                  <Select.Item index={0} value="all">
                    <Select.ItemText>All Locations</Select.ItemText>
                  </Select.Item>
                  <Select.Item index={1} value="fridge">
                    <Select.ItemText>❄️ Fridge</Select.ItemText>
                  </Select.Item>
                  <Select.Item index={2} value="freezer">
                    <Select.ItemText>🧊 Freezer</Select.ItemText>
                  </Select.Item>
                  <Select.Item index={3} value="pantry">
                    <Select.ItemText>🥫 Pantry</Select.ItemText>
                  </Select.Item>
                  <Select.Item index={4} value="counter">
                    <Select.ItemText>🍌 Counter</Select.ItemText>
                  </Select.Item>
                  <Select.Item index={5} value="garden">
                    <Select.ItemText>🌱 Garden</Select.ItemText>
                  </Select.Item>
                </Select.Viewport>
              </Select.Content>
            </Select>
          </XStack>

          {/* Expiring Warning */}
          {expiringCount > 0 && (
            <XStack
              marginTop="$2"
              padding="$2"
              backgroundColor="$yellow3"
              borderRadius="$3"
              alignItems="center"
              space="$2"
            >
              <Text>⚠️</Text>
              <Text color="$yellow11" fontSize="$3">
                {expiringCount} item{expiringCount > 1 ? 's' : ''} expiring soon
              </Text>
            </XStack>
          )}
        </YStack>

        {/* Item List */}
        {isLoading ? (
          <YStack flex={1} justifyContent="center" alignItems="center">
            <Spinner size="large" color="$blue10" />
            <Text marginTop="$3" color="$gray10">Loading pantry...</Text>
          </YStack>
        ) : processedItems.length === 0 ? (
          <YStack flex={1} justifyContent="center" alignItems="center" padding="$6">
            <Package size={64} color="#ccc" />
            <Text fontSize="$6" marginTop="$4" textAlign="center">
              {searchQuery || filterLocation !== 'all'
                ? 'No matching items'
                : 'Your pantry is empty'}
            </Text>
            <Text color="$gray10" textAlign="center" marginTop="$2">
              {searchQuery || filterLocation !== 'all'
                ? 'Try adjusting your filters'
                : 'Tap the + button to add items'}
            </Text>
            {!searchQuery && filterLocation === 'all' && (
              <Button
                testID="add-first-item"
                size="$5"
                theme="blue"
                marginTop="$4"
                icon={<Plus size={20} />}
                onPress={() => setShowActionSheet(true)}
              >
                Add First Item
              </Button>
            )}
          </YStack>
        ) : (
          <FlatList
            data={sortedLocations}
            keyExtractor={(location) => location}
            refreshControl={
              <RefreshControl refreshing={isRefetching} onRefresh={refetch} />
            }
            contentContainerStyle={{ paddingBottom: 80 }}
            renderItem={({ item: location }) => (
              <YStack padding="$3" testID={`location-${location}`}>
                <Text
                  fontSize="$5"
                  fontWeight="bold"
                  marginBottom="$2"
                  color="$gray11"
                >
                  {getLocationEmoji(location)} {location.charAt(0).toUpperCase() + location.slice(1)}
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

        {/* FAB */}
        <FAB
          testID="scan-item-fab"
          icon={<Camera size={24} color="white" />}
          backgroundColor="$blue10"
          onPress={() => router.push('/(app)/inventory/scan-result')}
        />

        {/* Add Options Sheet */}
        <Sheet
          modal
          open={showActionSheet}
          onOpenChange={setShowActionSheet}
          snapPoints={[35]}
          dismissOnSnapToBottom
        >
          <Sheet.Overlay />
          <Sheet.Frame padding="$4">
            <Sheet.Handle />
            <YStack space="$3" marginTop="$4">
              <Text fontSize="$6" fontWeight="bold">Add Item</Text>
              
              <Button
                testID="scan-item-option"
                size="$5"
                icon={<Camera size={20} />}
                onPress={() => {
                  setShowActionSheet(false);
                  router.push('/(app)/inventory/scan-result');
                }}
              >
                Scan with Camera
              </Button>
              
              <Button
                testID="manual-add-option"
                size="$5"
                chromeless
                icon={<Plus size={20} />}
                onPress={() => {
                  setShowActionSheet(false);
                  setIsAddSheetOpen(true);
                }}
              >
                Add Manually
              </Button>
            </YStack>
          </Sheet.Frame>
        </Sheet>

        {/* Add Item Sheet */}
        <AddItemSheet
          open={isAddSheetOpen}
          onOpenChange={setIsAddSheetOpen}
          householdId={householdId}
        />
      </YStack>
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
    onError: (error) => {
      console.error('❌ Failed to add item:', error);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pantry', householdId] });
      onOpenChange(false);
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
            testID="item-name-input"
            size="$4"
            placeholder="Item name (e.g., Milk)"
            value={name}
            onChangeText={setName}
            autoFocus
          />
          
          <XStack space="$3">
            <Input
              testID="item-qty-input"
              flex={1}
              size="$4"
              placeholder="Qty"
              keyboardType="numeric"
              value={quantity}
              onChangeText={setQuantity}
            />
            <Input
              testID="item-unit-input"
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
                testID={`location-${loc}`}
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
            testID="save-item-button"
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

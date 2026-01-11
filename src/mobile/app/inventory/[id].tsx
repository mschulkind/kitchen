/**
 * Inventory Item Detail/Edit Screen ✏️
 * 
 * View and edit a single pantry item.
 */

import { useState, useEffect } from 'react';
import { Alert } from 'react-native';
import { useLocalSearchParams, useRouter, Stack } from 'expo-router';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  YStack,
  XStack,
  Text,
  H1,
  Input,
  Button,
  Spinner,
  Card,
} from 'tamagui';
import { Save, Trash2 } from '@tamagui/lucide-icons';

import { supabase, Database } from '@/lib/supabase';
import { useHouseholdId } from '@/hooks/useInventorySubscription';

type PantryItem = Database['public']['Tables']['pantry_items']['Row'];
type PantryLocation = PantryItem['location'];

export default function InventoryItemScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const householdId = useHouseholdId();

  // Form state
  const [name, setName] = useState('');
  const [quantity, setQuantity] = useState('');
  const [unit, setUnit] = useState('');
  const [location, setLocation] = useState<PantryLocation>('pantry');
  const [expiryDate, setExpiryDate] = useState('');
  const [notes, setNotes] = useState('');

  // Fetch item
  const { data: item, isLoading } = useQuery({
    queryKey: ['pantry-item', id],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('pantry_items')
        .select('*')
        .eq('id', id)
        .single();
      
      if (error) throw error;
      return data as PantryItem;
    },
    enabled: !!id,
  });

  // Populate form when item loads
  useEffect(() => {
    if (item) {
      setName(item.name);
      setQuantity(String(item.quantity));
      setUnit(item.unit);
      setLocation(item.location);
      setExpiryDate(item.expiry_date || '');
      setNotes(item.notes || '');
    }
  }, [item]);

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: async () => {
      const { error } = await supabase
        .from('pantry_items')
        .update({
          name,
          quantity: parseFloat(quantity) || 0,
          unit,
          location,
          expiry_date: expiryDate || null,
          notes: notes || null,
        })
        .eq('id', id);
      
      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pantry', householdId] });
      queryClient.invalidateQueries({ queryKey: ['pantry-item', id] });
      router.back();
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async () => {
      const { error } = await supabase
        .from('pantry_items')
        .delete()
        .eq('id', id);
      
      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pantry', householdId] });
      router.back();
    },
  });

  const handleDelete = () => {
    Alert.alert(
      'Delete Item',
      `Are you sure you want to delete "${name}"?`,
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Delete', 
          style: 'destructive', 
          onPress: () => deleteMutation.mutate() 
        },
      ]
    );
  };

  if (isLoading) {
    return (
      <YStack flex={1} justifyContent="center" alignItems="center">
        <Spinner size="large" />
      </YStack>
    );
  }

  return (
    <>
      <Stack.Screen options={{ title: 'Edit Item' }} />
      
      <YStack flex={1} padding="$4" backgroundColor="$background">
        <Card elevate padding="$4">
          <YStack space="$4">
            <YStack>
              <Text fontSize="$2" color="$gray10" marginBottom="$1">Name</Text>
              <Input
                size="$4"
                value={name}
                onChangeText={setName}
                placeholder="Item name"
              />
            </YStack>

            <XStack space="$3">
              <YStack flex={1}>
                <Text fontSize="$2" color="$gray10" marginBottom="$1">Quantity</Text>
                <Input
                  size="$4"
                  value={quantity}
                  onChangeText={setQuantity}
                  keyboardType="numeric"
                  placeholder="1"
                />
              </YStack>
              <YStack flex={2}>
                <Text fontSize="$2" color="$gray10" marginBottom="$1">Unit</Text>
                <Input
                  size="$4"
                  value={unit}
                  onChangeText={setUnit}
                  placeholder="count, kg, ml..."
                />
              </YStack>
            </XStack>

            <YStack>
              <Text fontSize="$2" color="$gray10" marginBottom="$2">Location</Text>
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
            </YStack>

            <YStack>
              <Text fontSize="$2" color="$gray10" marginBottom="$1">Expiry Date</Text>
              <Input
                size="$4"
                value={expiryDate}
                onChangeText={setExpiryDate}
                placeholder="YYYY-MM-DD"
              />
            </YStack>

            <YStack>
              <Text fontSize="$2" color="$gray10" marginBottom="$1">Notes</Text>
              <Input
                size="$4"
                value={notes}
                onChangeText={setNotes}
                placeholder="Optional notes..."
                multiline
                numberOfLines={3}
              />
            </YStack>
          </YStack>
        </Card>

        <YStack marginTop="$4" space="$3">
          <Button
            size="$5"
            theme="green"
            icon={updateMutation.isPending ? <Spinner /> : <Save size={20} />}
            disabled={!name.trim() || updateMutation.isPending}
            onPress={() => updateMutation.mutate()}
          >
            Save Changes
          </Button>
          
          <Button
            size="$5"
            theme="red"
            icon={deleteMutation.isPending ? <Spinner /> : <Trash2 size={20} />}
            disabled={deleteMutation.isPending}
            onPress={handleDelete}
          >
            Delete Item
          </Button>
        </YStack>
      </YStack>
    </>
  );
}

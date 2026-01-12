/**
 * Vision Staging Screen 📸
 * 
 * Review and edit AI-detected items before committing to pantry.
 * Per frontend-redesign.md Section 2.5 (Phase 4)
 * 
 * Fun fact: Computer vision can identify 1000+ grocery items! 🤖
 */

import { useState, useEffect } from 'react';
import { ScrollView } from 'react-native';
import { useRouter, Stack } from 'expo-router';
import { useMutation, useQueryClient } from '@tanstack/react-query';
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
} from 'tamagui';
import {
  Check,
  Trash2,
  Edit3,
  Camera,
  RefreshCw,
} from '@tamagui/lucide-icons';

import { supabase } from '@/lib/supabase';
import { useHouseholdId } from '@/hooks/useInventorySubscription';
import { KitchenButton } from '@/components/Core/Button';

type DetectedItem = {
  id: string;
  name: string;
  quantity: string;
  unit: string;
  confidence: number;
  editing: boolean;
};

// Mock data for demo - in production this comes from Vision API
const MOCK_DETECTED_ITEMS: DetectedItem[] = [
  { id: '1', name: 'Milk', quantity: '1', unit: 'gallon', confidence: 0.95, editing: false },
  { id: '2', name: 'Eggs', quantity: '12', unit: 'count', confidence: 0.92, editing: false },
  { id: '3', name: 'Butter', quantity: '1', unit: 'lb', confidence: 0.88, editing: false },
  { id: '4', name: 'Bread', quantity: '1', unit: 'loaf', confidence: 0.85, editing: false },
  { id: '5', name: 'Cheese', quantity: '8', unit: 'oz', confidence: 0.78, editing: false },
];

export default function ScanResultScreen() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const householdId = useHouseholdId();
  
  const [items, setItems] = useState<DetectedItem[]>([]);
  const [isScanning, setIsScanning] = useState(true);

  // Simulate vision processing
  useEffect(() => {
    const timer = setTimeout(() => {
      setItems(MOCK_DETECTED_ITEMS);
      setIsScanning(false);
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  // Toggle edit mode for item
  const toggleEdit = (id: string) => {
    setItems((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, editing: !item.editing } : item
      )
    );
  };

  // Update item field
  const updateItem = (id: string, field: keyof DetectedItem, value: string) => {
    setItems((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, [field]: value } : item
      )
    );
  };

  // Remove item
  const removeItem = (id: string) => {
    setItems((prev) => prev.filter((item) => item.id !== id));
  };

  // Confirm all mutation
  const confirmAll = useMutation({
    mutationFn: async () => {
      if (!householdId) throw new Error('No household');

      const toInsert = items.map((item) => ({
        household_id: householdId,
        name: item.name,
        quantity: parseFloat(item.quantity) || 1,
        unit: item.unit,
        location: 'fridge' as const, // Default for scanned items
      }));

      const { error } = await supabase.from('pantry_items').insert(toInsert);
      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pantry'] });
      router.back();
    },
  });

  // Re-scan
  const handleRescan = () => {
    setIsScanning(true);
    setItems([]);
    setTimeout(() => {
      setItems(MOCK_DETECTED_ITEMS);
      setIsScanning(false);
    }, 2000);
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return '$green10';
    if (confidence >= 0.7) return '$yellow10';
    return '$red10';
  };

  return (
    <>
      <Stack.Screen
        options={{
          headerRight: () => (
            <Button
              size="$3"
              chromeless
              onPress={() => router.back()}
            >
              Cancel
            </Button>
          ),
        }}
      />

      <YStack flex={1} backgroundColor="$background">
        {isScanning ? (
          <YStack flex={1} justifyContent="center" alignItems="center" padding="$6">
            <Camera size={60} color="$blue10" />
            <Spinner size="large" color="$blue10" marginTop="$4" />
            <H3 marginTop="$4" color="$gray11">
              Analyzing image...
            </H3>
            <Paragraph color="$gray10" textAlign="center" marginTop="$2">
              Our AI is identifying items in your photo
            </Paragraph>
          </YStack>
        ) : items.length === 0 ? (
          <YStack flex={1} justifyContent="center" alignItems="center" padding="$6">
            <Text fontSize="$8">🤷</Text>
            <H3 marginTop="$4" color="$gray11">
              No items detected
            </H3>
            <Paragraph color="$gray10" textAlign="center" marginTop="$2">
              Try taking another photo with better lighting
            </Paragraph>
            <Button
              testID="rescan-button"
              marginTop="$4"
              icon={<RefreshCw size={18} />}
              onPress={handleRescan}
            >
              Try Again
            </Button>
          </YStack>
        ) : (
          <>
            <ScrollView contentContainerStyle={{ padding: 16, paddingBottom: 100 }}>
              <YStack space="$4">
                <YStack>
                  <H2 testID="detected-count">
                    {items.length} Item{items.length !== 1 ? 's' : ''} Detected
                  </H2>
                  <Paragraph color="$gray10">
                    Review and edit before adding to your pantry
                  </Paragraph>
                </YStack>

                {/* Detected Items */}
                <YStack space="$3">
                  {items.map((item, idx) => (
                    <Card
                      key={item.id}
                      bordered
                      padding="$3"
                      testID={`detected-item-${idx}`}
                    >
                      {item.editing ? (
                        // Edit Mode
                        <YStack space="$2">
                          <Input
                            testID={`edit-name-${idx}`}
                            placeholder="Item name"
                            value={item.name}
                            onChangeText={(v) => updateItem(item.id, 'name', v)}
                          />
                          <XStack space="$2">
                            <Input
                              testID={`edit-qty-${idx}`}
                              flex={1}
                              placeholder="Qty"
                              value={item.quantity}
                              onChangeText={(v) => updateItem(item.id, 'quantity', v)}
                              keyboardType="numeric"
                            />
                            <Input
                              testID={`edit-unit-${idx}`}
                              flex={1}
                              placeholder="Unit"
                              value={item.unit}
                              onChangeText={(v) => updateItem(item.id, 'unit', v)}
                            />
                          </XStack>
                          <XStack justifyContent="flex-end" space="$2">
                            <Button
                              testID={`save-edit-${idx}`}
                              size="$3"
                              theme="green"
                              icon={<Check size={16} />}
                              onPress={() => toggleEdit(item.id)}
                            >
                              Done
                            </Button>
                          </XStack>
                        </YStack>
                      ) : (
                        // View Mode
                        <XStack alignItems="center" space="$3">
                          {/* Confidence Indicator */}
                          <YStack
                            width={8}
                            height={40}
                            borderRadius={4}
                            backgroundColor={getConfidenceColor(item.confidence)}
                          />

                          {/* Item Info */}
                          <YStack flex={1}>
                            <Text fontWeight="600" fontSize="$5">
                              {item.name}
                            </Text>
                            <Text color="$gray10" fontSize="$3">
                              {item.quantity} {item.unit}
                            </Text>
                          </YStack>

                          {/* Confidence Badge */}
                          <Text
                            fontSize="$2"
                            color={getConfidenceColor(item.confidence)}
                          >
                            {Math.round(item.confidence * 100)}%
                          </Text>

                          {/* Actions */}
                          <Button
                            testID={`edit-item-${idx}`}
                            size="$2"
                            circular
                            chromeless
                            icon={<Edit3 size={16} color="$gray10" />}
                            onPress={() => toggleEdit(item.id)}
                          />
                          <Button
                            testID={`remove-item-${idx}`}
                            size="$2"
                            circular
                            chromeless
                            icon={<Trash2 size={16} color="$red10" />}
                            onPress={() => removeItem(item.id)}
                          />
                        </XStack>
                      )}
                    </Card>
                  ))}
                </YStack>

                {/* Rescan Option */}
                <Button
                  testID="rescan-button"
                  size="$4"
                  chromeless
                  icon={<RefreshCw size={18} />}
                  onPress={handleRescan}
                >
                  Scan Again
                </Button>
              </YStack>
            </ScrollView>

            {/* Confirm Button */}
            <YStack
              position="absolute"
              bottom={0}
              left={0}
              right={0}
              padding="$4"
              backgroundColor="$background"
              borderTopWidth={1}
              borderTopColor="$gray4"
            >
              <KitchenButton
                testID="confirm-all-button"
                size="$5"
                theme="green"
                icon={
                  confirmAll.isPending ? (
                    <Spinner size="small" color="white" />
                  ) : (
                    <Check size={20} />
                  )
                }
                onPress={() => confirmAll.mutate()}
                disabled={confirmAll.isPending || items.length === 0}
              >
                {confirmAll.isPending
                  ? 'Adding...'
                  : `Confirm All (${items.length})`}
              </KitchenButton>
            </YStack>
          </>
        )}
      </YStack>
    </>
  );
}

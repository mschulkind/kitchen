/**
 * Stock Check Screen 🔍
 * 
 * Verify ingredient availability before cooking.
 * Shows three sections: Have (Enough), Have (Not Enough), Missing.
 * Per frontend-redesign.md Section 2.3 and Phase 3.
 * 
 * Fun fact: Planning ingredients reduces food waste by 25%! 🌱
 */

import { useState, useEffect, useMemo } from 'react';
import { ScrollView } from 'react-native';
import { useLocalSearchParams, useRouter, Stack } from 'expo-router';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  YStack,
  XStack,
  H2,
  H3,
  Text,
  Paragraph,
  Button,
  Card,
  Spinner,
  Checkbox,
} from 'tamagui';
import {
  CheckCircle2,
  AlertCircle,
  XCircle,
  Plus,
  ShoppingCart,
} from '@tamagui/lucide-icons';

import { supabase } from '@/lib/supabase';
import { KitchenButton } from '@/components/Core/Button';

type Ingredient = {
  order: number;
  name: string;
  quantity: string;
  unit: string;
};

type StockStatus = 'have-enough' | 'have-partial' | 'missing';

type IngredientWithStatus = Ingredient & {
  status: StockStatus;
  pantryQuantity?: number;
  pantryUnit?: string;
};

export default function CheckStockScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  
  const [ingredientStatuses, setIngredientStatuses] = useState<
    Record<string, StockStatus>
  >({});

  // Fetch recipe
  const { data: recipe, isLoading: recipeLoading } = useQuery({
    queryKey: ['recipe', id],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('recipes')
        .select('id, title, ingredients_json')
        .eq('id', id)
        .single();
      if (error) throw error;
      return data;
    },
    enabled: !!id,
  });

  // Fetch pantry items for comparison
  const { data: pantryItems, isLoading: pantryLoading } = useQuery({
    queryKey: ['pantry'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('pantry_items')
        .select('name, quantity, unit');
      if (error) throw error;
      return data;
    },
  });

  // Calculate initial statuses based on pantry
  useEffect(() => {
    if (!recipe?.ingredients_json || !pantryItems) return;

    const statuses: Record<string, StockStatus> = {};
    
    recipe.ingredients_json.forEach((ingredient: Ingredient, idx: number) => {
      const key = `${idx}-${ingredient.name}`;
      const pantryMatch = pantryItems.find(
        (p) => p.name.toLowerCase() === ingredient.name.toLowerCase()
      );

      if (pantryMatch) {
        // Simple comparison - in production, use unit conversion
        const neededQty = parseFloat(ingredient.quantity) || 1;
        const haveQty = pantryMatch.quantity || 0;
        
        if (haveQty >= neededQty) {
          statuses[key] = 'have-enough';
        } else if (haveQty > 0) {
          statuses[key] = 'have-partial';
        } else {
          statuses[key] = 'missing';
        }
      } else {
        statuses[key] = 'missing';
      }
    });

    setIngredientStatuses(statuses);
  }, [recipe, pantryItems]);

  // Add to pantry mutation (Lazy Discovery)
  const addToPantry = useMutation({
    mutationFn: async (ingredient: Ingredient) => {
      const { error } = await supabase.from('pantry_items').insert({
        name: ingredient.name,
        quantity: parseFloat(ingredient.quantity) || 1,
        unit: ingredient.unit || 'item',
        location: 'pantry',
      });
      if (error) throw error;
    },
    onSuccess: (_, ingredient) => {
      const key = Object.keys(ingredientStatuses).find((k) =>
        k.endsWith(`-${ingredient.name}`)
      );
      if (key) {
        setIngredientStatuses((prev) => ({
          ...prev,
          [key]: 'have-enough',
        }));
      }
      queryClient.invalidateQueries({ queryKey: ['pantry'] });
    },
  });

  // Add to shopping list mutation
  const addToShoppingList = useMutation({
    mutationFn: async (ingredients: Ingredient[]) => {
      const items = ingredients.map((i) => ({
        name: i.name,
        quantity: i.quantity,
        unit: i.unit,
        checked: false,
      }));
      const { error } = await supabase.from('shopping_list').insert(items);
      if (error) throw error;
    },
    onSuccess: () => {
      router.push('/(app)/shopping');
    },
  });

  // Group ingredients by status
  const groupedIngredients = useMemo(() => {
    if (!recipe?.ingredients_json) return { have: [], partial: [], missing: [] };

    const have: IngredientWithStatus[] = [];
    const partial: IngredientWithStatus[] = [];
    const missing: IngredientWithStatus[] = [];

    recipe.ingredients_json.forEach((ingredient: Ingredient, idx: number) => {
      const key = `${idx}-${ingredient.name}`;
      const status = ingredientStatuses[key] || 'missing';
      const item = { ...ingredient, status };

      switch (status) {
        case 'have-enough':
          have.push(item);
          break;
        case 'have-partial':
          partial.push(item);
          break;
        default:
          missing.push(item);
      }
    });

    return { have, partial, missing };
  }, [recipe, ingredientStatuses]);

  if (recipeLoading || pantryLoading) {
    return (
      <YStack flex={1} justifyContent="center" alignItems="center">
        <Spinner size="large" color="$blue10" />
        <Text marginTop="$2" color="$gray10">
          Checking your pantry...
        </Text>
      </YStack>
    );
  }

  const missingIngredients = [
    ...groupedIngredients.missing,
    ...groupedIngredients.partial,
  ];

  return (
    <>
      <Stack.Screen options={{ title: `Check Stock` }} />

      <ScrollView contentContainerStyle={{ padding: 16, paddingBottom: 100 }}>
        <YStack space="$4">
          <Paragraph color="$gray10">
            Tap "I have this" on missing items to add them to your pantry.
          </Paragraph>

          {/* You Have (Enough) */}
          <YStack testID="have-section">
            <XStack space="$2" alignItems="center" marginBottom="$2">
              <CheckCircle2 size={20} color="#16a34a" />
              <H3 color="$green11">You Have ({groupedIngredients.have.length})</H3>
            </XStack>
            {groupedIngredients.have.length === 0 ? (
              <Card bordered padding="$3" backgroundColor="$gray2">
                <Text color="$gray10">No items matched your pantry</Text>
              </Card>
            ) : (
              <Card bordered>
                {groupedIngredients.have.map((item, idx) => (
                  <XStack
                    key={idx}
                    padding="$3"
                    borderBottomWidth={
                      idx < groupedIngredients.have.length - 1 ? 1 : 0
                    }
                    borderBottomColor="$gray4"
                    testID={`have-item-${idx}`}
                  >
                    <CheckCircle2 size={18} color="#16a34a" />
                    <Text flex={1} marginLeft="$2">
                      {item.name}
                    </Text>
                    <Text color="$gray10">
                      {item.quantity} {item.unit}
                    </Text>
                  </XStack>
                ))}
              </Card>
            )}
          </YStack>

          {/* You Have (Not Enough) */}
          {groupedIngredients.partial.length > 0 && (
            <YStack testID="low-section">
              <XStack space="$2" alignItems="center" marginBottom="$2">
                <AlertCircle size={20} color="#f59e0b" />
                <H3 color="$yellow11">
                  Low Stock ({groupedIngredients.partial.length})
                </H3>
              </XStack>
              <Card bordered>
                {groupedIngredients.partial.map((item, idx) => (
                  <XStack
                    key={idx}
                    padding="$3"
                    borderBottomWidth={
                      idx < groupedIngredients.partial.length - 1 ? 1 : 0
                    }
                    borderBottomColor="$gray4"
                    alignItems="center"
                    testID={`partial-item-${idx}`}
                  >
                    <AlertCircle size={18} color="#f59e0b" />
                    <Text flex={1} marginLeft="$2">
                      {item.name}
                    </Text>
                    <Text color="$gray10" marginRight="$2">
                      Need: {item.quantity} {item.unit}
                    </Text>
                  </XStack>
                ))}
              </Card>
            </YStack>
          )}

          {/* Missing */}
          <YStack testID="missing-section">
            <XStack space="$2" alignItems="center" marginBottom="$2">
              <XCircle size={20} color="#dc2626" />
              <H3 color="$red11">Missing ({groupedIngredients.missing.length})</H3>
            </XStack>
            {groupedIngredients.missing.length === 0 ? (
              <Card bordered padding="$3" backgroundColor="$green2">
                <Text color="$green11">🎉 You have everything you need!</Text>
              </Card>
            ) : (
              <Card bordered>
                {groupedIngredients.missing.map((item, idx) => (
                  <XStack
                    key={idx}
                    padding="$3"
                    borderBottomWidth={
                      idx < groupedIngredients.missing.length - 1 ? 1 : 0
                    }
                    borderBottomColor="$gray4"
                    alignItems="center"
                    testID={`missing-item-${idx}`}
                  >
                    <XCircle size={18} color="#dc2626" />
                    <Text flex={1} marginLeft="$2">
                      {item.name}
                    </Text>
                    <Text color="$gray10" marginRight="$2">
                      {item.quantity} {item.unit}
                    </Text>
                    <Button
                      size="$2"
                      theme="green"
                      icon={<Plus size={14} />}
                      onPress={() => addToPantry.mutate(item)}
                      testID={`add-to-pantry-${idx}`}
                    >
                      I have this
                    </Button>
                  </XStack>
                ))}
              </Card>
            )}
          </YStack>

          {/* Actions */}
          {missingIngredients.length > 0 && (
            <KitchenButton
              testID="add-to-shopping-button"
              theme="orange"
              icon={<ShoppingCart size={18} />}
              onPress={() =>
                addToShoppingList.mutate(missingIngredients)
              }
            >
              Add {missingIngredients.length} items to Shopping List
            </KitchenButton>
          )}
        </YStack>
      </ScrollView>
    </>
  );
}

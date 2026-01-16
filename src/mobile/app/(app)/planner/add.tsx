/**
 * Add Meal Screen ➕
 * 
 * Manually select a recipe for a specific meal slot.
 */

import { useState } from 'react';
import { ScrollView, FlatList } from 'react-native';
import { useLocalSearchParams, useRouter, Stack } from 'expo-router';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  YStack,
  XStack,
  Text,
  Paragraph,
  Button,
  Input,
  Card,
  Spinner,
} from 'tamagui';
import { Search, ChefHat, Check } from '@tamagui/lucide-icons';

import { supabase } from '@/lib/supabase';

export default function AddMealScreen() {
  const { date, meal_type = 'main' } = useLocalSearchParams<{ date: string, meal_type: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch all recipes
  const { data: recipes, isLoading } = useQuery({
    queryKey: ['recipes', searchQuery],
    queryFn: async () => {
      let query = supabase.from('recipes').select('*').order('title');
      
      if (searchQuery) {
        query = query.ilike('title', `%${searchQuery}%`);
      }
      
      const { data, error } = await query;
      if (error) throw error;
      return data;
    },
  });

  // Add meal mutation
  const addMeal = useMutation({
    mutationFn: async (recipeId: string) => {
      const { error } = await supabase.from('meal_plans').insert({
        date,
        meal_type,
        recipe_id: recipeId,
        locked: true,
      });
      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['meal_plans'] });
      router.back();
    },
  });

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
        <YStack padding="$4" space="$4">
          <Paragraph color="$gray10">
            Select a recipe for {date} ({meal_type})
          </Paragraph>

          <XStack
            alignItems="center"
            backgroundColor="$gray3"
            borderRadius="$4"
            paddingHorizontal="$3"
            space="$2"
          >
            <Search size={18} color="$gray10" />
            <Input
              testID="recipe-search-input"
              flex={1}
              placeholder="Search recipes..."
              value={searchQuery}
              onChangeText={setSearchQuery}
              borderWidth={0}
              backgroundColor="transparent"
              size="$4"
            />
          </XStack>
        </YStack>

        {isLoading ? (
          <YStack flex={1} justifyContent="center" alignItems="center">
            <Spinner size="large" color="$orange10" />
          </YStack>
        ) : (
          <FlatList
            data={recipes}
            keyExtractor={(item) => item.id}
            contentContainerStyle={{ padding: 16 }}
            renderItem={({ item }) => (
              <Card
                testID={`recipe-option-${item.id}`}
                bordered
                padding="$4"
                marginBottom="$3"
                pressStyle={{ scale: 0.98 }}
                onPress={() => addMeal.mutate(item.id)}
                disabled={addMeal.isPending}
              >
                <XStack space="$3" alignItems="center" justifyContent="space-between">
                  <XStack space="$3" alignItems="center" flex={1}>
                    <ChefHat size={24} color="$orange10" />
                    <YStack flex={1}>
                      <Text fontWeight="bold" color="$gray12">{item.title}</Text>
                      {item.cook_time_minutes && (
                        <Text fontSize="$2" color="$gray10">
                          {item.cook_time_minutes} min cook
                        </Text>
                      )}
                    </YStack>
                  </XStack>
                  {addMeal.isPending && addMeal.variables === item.id && (
                    <Spinner />
                  )}
                </XStack>
              </Card>
            )}
            ListEmptyComponent={
              <YStack alignItems="center" padding="$10">
                <Text color="$gray10">No recipes found</Text>
              </YStack>
            }
          />
        )}
      </YStack>
    </>
  );
}

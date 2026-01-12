/**
 * Plan Preview / "Choose Your Adventure" Screen 🎲
 * 
 * Display generated plan options with different themes.
 * Per frontend-redesign.md Section 2.4 (Phase 5)
 * 
 * Fun fact: Giving users 3 choices increases satisfaction by 40%! 🎯
 */

import { useState } from 'react';
import { ScrollView } from 'react-native';
import { useLocalSearchParams, useRouter, Stack } from 'expo-router';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  YStack,
  XStack,
  H1,
  H2,
  H3,
  Text,
  Paragraph,
  Button,
  Card,
  Spinner,
} from 'tamagui';
import { Check, Sparkles } from '@tamagui/lucide-icons';

import { supabase } from '@/lib/supabase';
import { KitchenButton } from '@/components/Core/Button';

type PlanOption = {
  id: string;
  theme: string;
  description: string;
  emoji: string;
};

export default function PlanPreviewScreen() {
  const { options: optionsParam } = useLocalSearchParams<{ options: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  
  const options: PlanOption[] = optionsParam
    ? JSON.parse(optionsParam)
    : [
        {
          id: '1',
          theme: 'Comfort Classics',
          description: 'Hearty, familiar dishes that feel like home.',
          emoji: '🍝',
        },
        {
          id: '2',
          theme: 'Global Explorer',
          description: 'Travel the world through your taste buds.',
          emoji: '🌍',
        },
        {
          id: '3',
          theme: 'Healthy & Fresh',
          description: 'Light, nutritious meals for peak energy.',
          emoji: '🥗',
        },
      ];

  const [selectedId, setSelectedId] = useState<string | null>(null);

  // Apply plan mutation
  const applyPlan = useMutation({
    mutationFn: async (optionId: string) => {
      // In production, call the API to generate and save the meal plan
      // based on the selected theme
      await new Promise((r) => setTimeout(r, 1500));
      
      // Mock: Insert meal plan entries
      const today = new Date();
      const meals = [];
      
      for (let i = 0; i < 3; i++) {
        const date = new Date(today);
        date.setDate(date.getDate() + i);
        
        meals.push({
          date: date.toISOString().split('T')[0],
          meal_type: 'main',
          recipe_id: `mock-recipe-${i}`,
          locked: false,
        });
      }

      // In real implementation:
      // const { error } = await supabase.from('meal_plans').insert(meals);
      // if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['meal_plans'] });
      router.replace('/(app)/planner');
    },
  });

  const handleSelect = (id: string) => {
    setSelectedId(id);
  };

  const handleConfirm = () => {
    if (selectedId) {
      applyPlan.mutate(selectedId);
    }
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

      <ScrollView contentContainerStyle={{ padding: 16, paddingBottom: 100 }}>
        <YStack space="$4">
          <YStack alignItems="center" marginBottom="$4">
            <H1 size="$8" textAlign="center">
              🎲 Choose Your Adventure
            </H1>
            <Paragraph color="$gray10" textAlign="center" marginTop="$2">
              Pick a theme for your meal plan
            </Paragraph>
          </YStack>

          {/* Option Cards */}
          <YStack space="$3">
            {options.map((option) => (
              <Card
                key={option.id}
                testID={`option-${option.id}`}
                bordered
                elevate={selectedId === option.id}
                backgroundColor={
                  selectedId === option.id ? '$green2' : '$background'
                }
                borderColor={selectedId === option.id ? '$green8' : '$gray6'}
                borderWidth={2}
                padding="$4"
                pressStyle={{ scale: 0.98 }}
                onPress={() => handleSelect(option.id)}
              >
                <XStack space="$3" alignItems="center">
                  <Text fontSize="$9">{option.emoji}</Text>
                  <YStack flex={1}>
                    <H3 color="$gray12">{option.theme}</H3>
                    <Paragraph color="$gray10" fontSize="$3">
                      {option.description}
                    </Paragraph>
                  </YStack>
                  {selectedId === option.id && (
                    <Check size={24} color="$green10" />
                  )}
                </XStack>
              </Card>
            ))}
          </YStack>

          {/* Confirm Button */}
          <KitchenButton
            testID="confirm-plan-button"
            size="$5"
            theme="green"
            marginTop="$4"
            icon={
              applyPlan.isPending ? (
                <Spinner size="small" color="white" />
              ) : (
                <Sparkles size={20} />
              )
            }
            onPress={handleConfirm}
            disabled={!selectedId || applyPlan.isPending}
          >
            {applyPlan.isPending ? 'Creating Plan...' : 'Apply This Plan'}
          </KitchenButton>
        </YStack>
      </ScrollView>
    </>
  );
}

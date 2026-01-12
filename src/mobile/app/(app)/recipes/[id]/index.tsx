/**
 * Recipe Detail Screen 📖
 * 
 * Full recipe view with ingredients, steps, and actions.
 * Per frontend-redesign.md Section 2.3
 * 
 * Fun fact: Recipe photos increase the chance of someone cooking it by 60%! 📸
 */

import { useLocalSearchParams, useRouter, Stack } from 'expo-router';
import { ScrollView, Dimensions } from 'react-native';
import { useQuery } from '@tanstack/react-query';
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
  Image,
  Spinner,
  Separator,
} from 'tamagui';
import {
  ChefHat,
  Clock,
  Users,
  CheckCircle,
  ShoppingCart,
  Edit3,
  Trash2,
} from '@tamagui/lucide-icons';

import { supabase } from '@/lib/supabase';
import { KitchenButton, FAB } from '@/components/Core/Button';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

type Ingredient = {
  order: number;
  name: string;
  quantity: string;
  unit: string;
};

type Step = {
  order: number;
  instruction: string;
};

type Recipe = {
  id: string;
  title: string;
  servings?: number;
  prep_time_minutes?: number;
  cook_time_minutes?: number;
  image_url?: string;
  source_url?: string;
  ingredients_json: Ingredient[];
  steps_json: Step[];
  created_at: string;
};

export default function RecipeDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();

  const { data: recipe, isLoading } = useQuery({
    queryKey: ['recipe', id],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('recipes')
        .select('*')
        .eq('id', id)
        .single();

      if (error) throw error;
      return data as Recipe;
    },
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <YStack flex={1} justifyContent="center" alignItems="center">
        <Spinner size="large" color="$orange10" />
      </YStack>
    );
  }

  if (!recipe) {
    return (
      <YStack flex={1} justifyContent="center" alignItems="center" padding="$6">
        <Text fontSize="$6">😕</Text>
        <H2 color="$gray11">Recipe not found</H2>
      </YStack>
    );
  }

  const totalTime =
    (recipe.prep_time_minutes || 0) + (recipe.cook_time_minutes || 0);

  return (
    <>
      <Stack.Screen options={{ title: recipe.title }} />

      <ScrollView contentContainerStyle={{ paddingBottom: 100 }}>
        {/* Hero Image */}
        {recipe.image_url && (
          <Image
            source={{ uri: recipe.image_url }}
            width={SCREEN_WIDTH}
            height={SCREEN_WIDTH * 0.6}
            resizeMode="cover"
          />
        )}

        <YStack padding="$4" space="$4">
          {/* Title & Meta */}
          <YStack>
            <H1 testID="recipe-title">{recipe.title}</H1>

            <XStack space="$4" marginTop="$2" flexWrap="wrap">
              {recipe.servings && (
                <XStack space="$1" alignItems="center">
                  <Users size={16} color="$gray10" />
                  <Text color="$gray10">{recipe.servings} servings</Text>
                </XStack>
              )}
              {recipe.prep_time_minutes && (
                <XStack space="$1" alignItems="center">
                  <Clock size={16} color="$gray10" />
                  <Text color="$gray10">{recipe.prep_time_minutes}m prep</Text>
                </XStack>
              )}
              {recipe.cook_time_minutes && (
                <XStack space="$1" alignItems="center">
                  <ChefHat size={16} color="$gray10" />
                  <Text color="$gray10">{recipe.cook_time_minutes}m cook</Text>
                </XStack>
              )}
            </XStack>
          </YStack>

          {/* Action Buttons */}
          <XStack space="$3">
            <KitchenButton
              testID="check-stock-button"
              flex={1}
              theme="blue"
              icon={<ShoppingCart size={18} />}
              onPress={() => router.push(`/(app)/recipes/${id}/check-stock`)}
            >
              Check Stock
            </KitchenButton>
          </XStack>

          <Separator />

          {/* Ingredients */}
          <YStack>
            <H3 testID="ingredients-section" marginBottom="$2">
              Ingredients
            </H3>
            <Card bordered padding="$3">
              {recipe.ingredients_json?.map((ingredient, idx) => (
                <XStack
                  key={idx}
                  paddingVertical="$2"
                  borderBottomWidth={
                    idx < recipe.ingredients_json.length - 1 ? 1 : 0
                  }
                  borderBottomColor="$gray4"
                  testID={`ingredient-${idx}`}
                >
                  <Text flex={1} color="$gray12">
                    {ingredient.name}
                  </Text>
                  <Text color="$gray10">
                    {ingredient.quantity} {ingredient.unit}
                  </Text>
                </XStack>
              ))}
            </Card>
          </YStack>

          {/* Instructions */}
          <YStack>
            <H3 testID="instructions-section" marginBottom="$2">
              Instructions
            </H3>
            <YStack space="$3">
              {recipe.steps_json?.map((step, idx) => (
                <XStack key={idx} space="$3" testID={`step-${idx}`}>
                  <YStack
                    width={32}
                    height={32}
                    borderRadius={16}
                    backgroundColor="$orange5"
                    justifyContent="center"
                    alignItems="center"
                  >
                    <Text fontWeight="bold" color="$orange11">
                      {step.order || idx + 1}
                    </Text>
                  </YStack>
                  <Paragraph flex={1} color="$gray12" lineHeight="$5">
                    {step.instruction}
                  </Paragraph>
                </XStack>
              ))}
            </YStack>
          </YStack>

          {/* Source Attribution */}
          {recipe.source_url && (
            <Card bordered padding="$3" backgroundColor="$gray2">
              <Text fontSize="$2" color="$gray10">
                📎 Source: {new URL(recipe.source_url).hostname}
              </Text>
            </Card>
          )}
        </YStack>
      </ScrollView>

      {/* Start Cooking FAB */}
      <FAB
        testID="start-cooking-fab"
        icon={<ChefHat size={24} color="white" />}
        backgroundColor="$green10"
        onPress={() => router.push(`/(app)/recipes/${id}/cook`)}
      />
    </>
  );
}

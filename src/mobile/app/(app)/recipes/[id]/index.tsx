/**
 * Recipe Detail Screen 📖
 * 
 * Full recipe view with ingredients, steps, and actions.
 * Per frontend-redesign.md Section 2.3
 * Now with AI image generation! 🖼️
 * 
 * Fun fact: Recipe photos increase the chance of someone cooking it by 60%! 📸
 */

import { useState } from 'react';
import { useLocalSearchParams, useRouter, Stack } from 'expo-router';
import { ScrollView, Dimensions, Platform, Alert } from 'react-native';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
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
  Image as ImageLucide,
  Wand2,
} from '@tamagui/lucide-icons';

import { KitchenButton, FAB } from '@/components/Core/Button';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

type Ingredient = {
  id: string;
  raw_text: string;
  item_name: string;
  quantity: number | null;
  unit: string | null;
  notes: string | null;
  sort_order: number;
};

type Recipe = {
  id: string;
  title: string;
  description?: string;
  servings?: number;
  prep_time_minutes?: number;
  cook_time_minutes?: number;
  image_url?: string;
  source_url?: string;
  instructions?: string[];
  ingredients?: Ingredient[];
  created_at: string;
};

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:5300';

export default function RecipeDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [generatedImageUrl, setGeneratedImageUrl] = useState<string | null>(null);

  const { data: recipe, isLoading } = useQuery({
    queryKey: ['recipe', id],
    queryFn: async () => {
      const response = await fetch(`${API_URL}/api/v1/recipes/${id}`);
      if (!response.ok) throw new Error('Failed to fetch recipe');
      return response.json() as Promise<Recipe>;
    },
    enabled: !!id,
  });

  // Image generation mutation
  const generateImageMutation = useMutation({
    mutationFn: async () => {
      const apiUrl = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:5300';
      const response = await fetch(`${apiUrl}/api/v1/recipes/${id}/generate-image`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ style: 'professional' }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate image');
      }
      
      return response.json();
    },
    onSuccess: (data) => {
      if (data.success && data.image_url) {
        setGeneratedImageUrl(data.image_url);
        // Invalidate recipe query to refresh
        queryClient.invalidateQueries({ queryKey: ['recipe', id] });
      }
    },
  });

  // Delete recipe mutation
  const deleteRecipeMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch(`${API_URL}/api/v1/recipes/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Failed to delete recipe');
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recipes'] });
      router.replace('/(app)/recipes');
    },
  });

  const handleDelete = () => {
    if (Platform.OS === 'web') {
      if (window.confirm(`Delete "${recipe?.title}"? This cannot be undone.`)) {
        deleteRecipeMutation.mutate();
      }
    } else {
      Alert.alert('Delete Recipe', `Delete "${recipe?.title}"? This cannot be undone.`, [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Delete', style: 'destructive', onPress: () => deleteRecipeMutation.mutate() },
      ]);
    }
  };

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

  const imageUrl = generatedImageUrl || recipe.image_url;
  const isGenerating = generateImageMutation.isPending;

  return (
    <>
      <Stack.Screen options={{ 
        title: recipe.title,
        headerRight: () => (
          <XStack space="$2">
            <Button
              testID="edit-recipe-button"
              size="$3"
              circular
              chromeless
              icon={<Edit3 size={20} color="$blue10" />}
              onPress={() => router.push(`/(app)/recipes/${id}/edit`)}
            />
            <Button
              testID="delete-recipe-button"
              size="$3"
              circular
              chromeless
              icon={<Trash2 size={20} color="$red10" />}
              onPress={handleDelete}
            />
          </XStack>
        ),
      }} />

      <ScrollView contentContainerStyle={{ paddingBottom: 100 }}>
        {/* Hero Image or Placeholder */}
        {imageUrl ? (
          <Image
            testID="recipe-hero-image"
            source={{ uri: imageUrl }}
            width={SCREEN_WIDTH}
            height={SCREEN_WIDTH * 0.6}
            resizeMode="cover"
          />
        ) : (
          <YStack
            testID="recipe-image-placeholder"
            width={SCREEN_WIDTH}
            height={SCREEN_WIDTH * 0.5}
            backgroundColor="$gray4"
            justifyContent="center"
            alignItems="center"
          >
            {isGenerating ? (
              <YStack alignItems="center" space="$2">
                <Spinner testID="image-generating-indicator" size="large" color="$orange10" />
                <Text color="$gray10">Generating appetizing image...</Text>
              </YStack>
            ) : (
              <YStack alignItems="center" space="$3">
                <ImageLucide size={64} color="$gray8" />
                <Text color="$gray10">No image yet</Text>
                <Button
                  testID="generate-image-button"
                  size="$3"
                  theme="orange"
                  icon={<Wand2 size={16} />}
                  onPress={() => generateImageMutation.mutate()}
                >
                  Generate with AI
                </Button>
              </YStack>
            )}
          </YStack>
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
              {recipe.ingredients?.map((ingredient, idx) => (
                <XStack
                  key={ingredient.id || idx}
                  paddingVertical="$2"
                  borderBottomWidth={
                    idx < (recipe.ingredients?.length ?? 0) - 1 ? 1 : 0
                  }
                  borderBottomColor="$gray4"
                  testID={`ingredient-${idx}`}
                >
                  <Text flex={1} color="$gray12">
                    {ingredient.item_name}
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
              {recipe.instructions?.map((step, idx) => (
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
                      {idx + 1}
                    </Text>
                  </YStack>
                  <Paragraph flex={1} color="$gray12" lineHeight="$5">
                    {step}
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

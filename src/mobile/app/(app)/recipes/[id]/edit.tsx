/**
 * Edit Recipe Screen ✏️
 * 
 * Edit existing recipe with pre-populated form.
 * Reuses the same form pattern as new.tsx.
 * 
 * Fun fact: The best recipes evolve over time — editing is how they improve! 🧪
 */

import { useState, useEffect } from 'react';
import { ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useLocalSearchParams, useRouter, Stack } from 'expo-router';
import {
  YStack,
  XStack,
  H3,
  Text,
  Button,
  Input,
  Separator,
  Spinner,
} from 'tamagui';
import { Plus, Trash2, Save } from '@tamagui/lucide-icons';

import { KitchenInput } from '@/components/Core/Input';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:5300';

type IngredientInput = {
  id: string;
  name: string;
  quantity: string;
  unit: string;
};

type StepInput = {
  id: string;
  instruction: string;
};

export default function EditRecipeScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();

  const [title, setTitle] = useState('');
  const [servings, setServings] = useState('4');
  const [prepTime, setPrepTime] = useState('');
  const [cookTime, setCookTime] = useState('');
  const [ingredients, setIngredients] = useState<IngredientInput[]>([
    { id: '1', name: '', quantity: '', unit: '' },
  ]);
  const [steps, setSteps] = useState<StepInput[]>([
    { id: '1', instruction: '' },
  ]);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [initialized, setInitialized] = useState(false);

  // Fetch existing recipe
  const { data: recipe, isLoading } = useQuery({
    queryKey: ['recipe', id],
    queryFn: async () => {
      const response = await fetch(`${API_URL}/api/v1/recipes/${id}`);
      if (!response.ok) throw new Error('Failed to fetch recipe');
      return response.json();
    },
    enabled: !!id,
  });

  // Pre-populate form when recipe loads
  useEffect(() => {
    if (recipe && !initialized) {
      setTitle(recipe.title || '');
      setServings(String(recipe.servings || 4));
      setPrepTime(recipe.prep_time_minutes ? String(recipe.prep_time_minutes) : '');
      setCookTime(recipe.cook_time_minutes ? String(recipe.cook_time_minutes) : '');

      if (recipe.ingredients?.length > 0) {
        setIngredients(
          recipe.ingredients.map((i: any, idx: number) => ({
            id: String(idx),
            name: i.item_name || i.name || '',
            quantity: i.quantity != null ? String(i.quantity) : '',
            unit: i.unit || '',
          }))
        );
      }

      if (recipe.instructions?.length > 0) {
        setSteps(
          recipe.instructions.map((instruction: string, idx: number) => ({
            id: String(idx),
            instruction,
          }))
        );
      }

      setInitialized(true);
    }
  }, [recipe, initialized]);

  // Save mutation
  const saveMutation = useMutation({
    mutationFn: async () => {
      const newErrors: Record<string, string> = {};
      if (!title.trim()) newErrors.title = 'Title is required';
      if (ingredients.every((i) => !i.name.trim())) {
        newErrors.ingredients = 'At least one ingredient is required';
      }
      if (steps.every((s) => !s.instruction.trim())) {
        newErrors.steps = 'At least one step is required';
      }

      if (Object.keys(newErrors).length > 0) {
        setErrors(newErrors);
        throw new Error('Validation failed');
      }

      const validIngredients = ingredients.filter((i) => i.name.trim());
      const validSteps = steps.filter((s) => s.instruction.trim());

      const response = await fetch(`${API_URL}/api/v1/recipes/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: title.trim(),
          servings: parseInt(servings) || 4,
          prep_time_minutes: prepTime ? parseInt(prepTime) : null,
          cook_time_minutes: cookTime ? parseInt(cookTime) : null,
          instructions: validSteps.map((s) => s.instruction.trim()),
          ingredient_texts: validIngredients.map((i) => {
            const parts = [i.name.trim()];
            if (i.quantity) parts.unshift(i.quantity);
            if (i.unit) parts.splice(1, 0, i.unit);
            return parts.join(' ');
          }),
        }),
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || 'Failed to update recipe');
      }
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recipe', id] });
      queryClient.invalidateQueries({ queryKey: ['recipes'] });
      router.back();
    },
  });

  // Ingredient helpers
  const addIngredient = () => {
    setIngredients([
      ...ingredients,
      { id: Date.now().toString(), name: '', quantity: '', unit: '' },
    ]);
  };

  const removeIngredient = (rid: string) => {
    if (ingredients.length > 1) {
      setIngredients(ingredients.filter((i) => i.id !== rid));
    }
  };

  const updateIngredient = (
    rid: string,
    field: keyof IngredientInput,
    value: string
  ) => {
    setIngredients(
      ingredients.map((i) => (i.id === rid ? { ...i, [field]: value } : i))
    );
  };

  // Step helpers
  const addStep = () => {
    setSteps([
      ...steps,
      { id: Date.now().toString(), instruction: '' },
    ]);
  };

  const removeStep = (sid: string) => {
    if (steps.length > 1) {
      setSteps(steps.filter((s) => s.id !== sid));
    }
  };

  const updateStep = (sid: string, instruction: string) => {
    setSteps(steps.map((s) => (s.id === sid ? { ...s, instruction } : s)));
  };

  if (isLoading) {
    return (
      <YStack flex={1} justifyContent="center" alignItems="center">
        <Spinner size="large" color="$orange10" />
      </YStack>
    );
  }

  return (
    <>
      <Stack.Screen
        options={{
          title: 'Edit Recipe',
          headerRight: () => (
            <Button
              testID="save-recipe-button"
              size="$3"
              theme="green"
              icon={<Save size={18} />}
              onPress={() => saveMutation.mutate()}
              disabled={saveMutation.isPending}
              marginRight="$2"
            >
              Save
            </Button>
          ),
        }}
      />

      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={{ flex: 1 }}
      >
        <ScrollView contentContainerStyle={{ padding: 16, paddingBottom: 100 }}>
          <YStack space="$4">
            {/* Title */}
            <KitchenInput
              testID="recipe-title-input"
              placeholder="Recipe Title"
              value={title}
              onChangeText={setTitle}
              error={errors.title}
              fontSize="$6"
              fontWeight="bold"
            />

            {/* Time & Servings Row */}
            <XStack space="$3">
              <YStack flex={1}>
                <Text fontSize="$2" color="$gray10" marginBottom="$1">
                  Servings
                </Text>
                <Input
                  testID="servings-input"
                  placeholder="4"
                  value={servings}
                  onChangeText={setServings}
                  keyboardType="numeric"
                />
              </YStack>
              <YStack flex={1}>
                <Text fontSize="$2" color="$gray10" marginBottom="$1">
                  Prep (min)
                </Text>
                <Input
                  testID="prep-time-input"
                  placeholder="15"
                  value={prepTime}
                  onChangeText={setPrepTime}
                  keyboardType="numeric"
                />
              </YStack>
              <YStack flex={1}>
                <Text fontSize="$2" color="$gray10" marginBottom="$1">
                  Cook (min)
                </Text>
                <Input
                  testID="cook-time-input"
                  placeholder="30"
                  value={cookTime}
                  onChangeText={setCookTime}
                  keyboardType="numeric"
                />
              </YStack>
            </XStack>

            <Separator marginVertical="$2" />

            {/* Ingredients Section */}
            <YStack>
              <XStack justifyContent="space-between" alignItems="center">
                <H3 testID="ingredients-header">Ingredients</H3>
                <Button
                  testID="add-ingredient-button"
                  size="$3"
                  circular
                  icon={<Plus size={18} />}
                  onPress={addIngredient}
                />
              </XStack>
              {errors.ingredients && (
                <Text color="$red10" fontSize="$2">
                  {errors.ingredients}
                </Text>
              )}

              <YStack space="$2" marginTop="$2">
                {ingredients.map((ingredient, index) => (
                  <XStack
                    key={ingredient.id}
                    space="$2"
                    alignItems="center"
                    testID={`ingredient-row-${index}`}
                  >
                    <Input
                      flex={1}
                      placeholder="Ingredient name"
                      value={ingredient.name}
                      onChangeText={(v) =>
                        updateIngredient(ingredient.id, 'name', v)
                      }
                      testID={`ingredient-name-${index}`}
                    />
                    <Input
                      width={60}
                      placeholder="Qty"
                      value={ingredient.quantity}
                      onChangeText={(v) =>
                        updateIngredient(ingredient.id, 'quantity', v)
                      }
                      testID={`ingredient-qty-${index}`}
                    />
                    <Input
                      width={70}
                      placeholder="Unit"
                      value={ingredient.unit}
                      onChangeText={(v) =>
                        updateIngredient(ingredient.id, 'unit', v)
                      }
                      testID={`ingredient-unit-${index}`}
                    />
                    <Button
                      size="$2"
                      circular
                      chromeless
                      icon={<Trash2 size={16} color="$red10" />}
                      onPress={() => removeIngredient(ingredient.id)}
                      disabled={ingredients.length === 1}
                    />
                  </XStack>
                ))}
              </YStack>
            </YStack>

            <Separator marginVertical="$2" />

            {/* Steps Section */}
            <YStack>
              <XStack justifyContent="space-between" alignItems="center">
                <H3 testID="instructions-header">Instructions</H3>
                <Button
                  testID="add-step-button"
                  size="$3"
                  circular
                  icon={<Plus size={18} />}
                  onPress={addStep}
                />
              </XStack>
              {errors.steps && (
                <Text color="$red10" fontSize="$2">
                  {errors.steps}
                </Text>
              )}

              <YStack space="$3" marginTop="$2">
                {steps.map((step, index) => (
                  <XStack
                    key={step.id}
                    space="$2"
                    alignItems="flex-start"
                    testID={`step-row-${index}`}
                  >
                    <YStack
                      width={28}
                      height={28}
                      borderRadius={14}
                      backgroundColor="$orange5"
                      justifyContent="center"
                      alignItems="center"
                      marginTop="$1"
                    >
                      <Text fontSize="$3" color="$orange11" fontWeight="bold">
                        {index + 1}
                      </Text>
                    </YStack>
                    <Input
                      flex={1}
                      multiline
                      numberOfLines={3}
                      placeholder={`Step ${index + 1} instructions...`}
                      value={step.instruction}
                      onChangeText={(v) => updateStep(step.id, v)}
                      testID={`step-instruction-${index}`}
                    />
                    <Button
                      size="$2"
                      circular
                      chromeless
                      icon={<Trash2 size={16} color="$red10" />}
                      onPress={() => removeStep(step.id)}
                      disabled={steps.length === 1}
                    />
                  </XStack>
                ))}
              </YStack>
            </YStack>
          </YStack>
        </ScrollView>
      </KeyboardAvoidingView>
    </>
  );
}

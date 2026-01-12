/**
 * New Recipe Form Screen 📝
 * 
 * Manual recipe entry with ingredients and steps arrays.
 * Per frontend-redesign.md Section 2.3
 * 
 * Fun fact: Writing down a recipe makes you 40% more likely to cook it! ✍️
 */

import { useState } from 'react';
import { ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter, Stack } from 'expo-router';
import {
  YStack,
  XStack,
  H1,
  H3,
  Text,
  Button,
  Input,
  Paragraph,
  Separator,
} from 'tamagui';
import { Plus, Trash2, GripVertical, Save } from '@tamagui/lucide-icons';

import { supabase } from '@/lib/supabase';
import { KitchenInput } from '@/components/Core/Input';
import { KitchenButton } from '@/components/Core/Button';
import { Screen } from '@/components/Layout/Screen';

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

export default function NewRecipeScreen() {
  const router = useRouter();
  const queryClient = useQueryClient();

  // Form state
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

  // Save mutation
  const saveMutation = useMutation({
    mutationFn: async () => {
      // Validate
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

      // Filter empty entries
      const validIngredients = ingredients.filter((i) => i.name.trim());
      const validSteps = steps.filter((s) => s.instruction.trim());

      // Save to Supabase
      const { data: recipe, error: recipeError } = await supabase
        .from('recipes')
        .insert({
          title: title.trim(),
          servings: parseInt(servings) || 4,
          prep_time_minutes: prepTime ? parseInt(prepTime) : null,
          cook_time_minutes: cookTime ? parseInt(cookTime) : null,
          ingredients_json: validIngredients.map((i, idx) => ({
            order: idx + 1,
            name: i.name.trim(),
            quantity: i.quantity.trim(),
            unit: i.unit.trim(),
          })),
          steps_json: validSteps.map((s, idx) => ({
            order: idx + 1,
            instruction: s.instruction.trim(),
          })),
        })
        .select()
        .single();

      if (recipeError) throw recipeError;
      return recipe;
    },
    onSuccess: () => {
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

  const removeIngredient = (id: string) => {
    if (ingredients.length > 1) {
      setIngredients(ingredients.filter((i) => i.id !== id));
    }
  };

  const updateIngredient = (
    id: string,
    field: keyof IngredientInput,
    value: string
  ) => {
    setIngredients(
      ingredients.map((i) => (i.id === id ? { ...i, [field]: value } : i))
    );
  };

  // Step helpers
  const addStep = () => {
    setSteps([
      ...steps,
      { id: Date.now().toString(), instruction: '' },
    ]);
  };

  const removeStep = (id: string) => {
    if (steps.length > 1) {
      setSteps(steps.filter((s) => s.id !== id));
    }
  };

  const updateStep = (id: string, instruction: string) => {
    setSteps(steps.map((s) => (s.id === id ? { ...s, instruction } : s)));
  };

  return (
    <>
      <Stack.Screen
        options={{
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

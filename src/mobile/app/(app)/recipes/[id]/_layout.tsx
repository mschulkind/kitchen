/**
 * Recipe Detail Layout 📖
 * 
 * Nested stack for recipe detail, check-stock, and cooking mode.
 */

import { Stack } from 'expo-router';

export default function RecipeDetailLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: true,
        animation: 'slide_from_right',
      }}
    >
      <Stack.Screen
        name="index"
        options={{
          title: 'Recipe',
        }}
      />
      <Stack.Screen
        name="check-stock"
        options={{
          title: 'Check Stock',
          presentation: 'modal',
        }}
      />
      <Stack.Screen
        name="cook"
        options={{
          title: 'Cooking',
          headerShown: false,
          presentation: 'fullScreenModal',
        }}
      />
    </Stack>
  );
}

/**
 * Recipe Routes Layout 📖
 * 
 * Stack navigator for the recipes module.
 * Includes list, detail, new, check-stock, and cooking screens.
 */

import { Stack } from 'expo-router';

export default function RecipesLayout() {
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
          title: 'Recipes',
          headerLargeTitle: true,
        }}
      />
      <Stack.Screen
        name="new"
        options={{
          title: 'New Recipe',
          presentation: 'modal',
        }}
      />
      <Stack.Screen
        name="[id]"
        options={{
          title: 'Recipe',
          headerShown: true,
        }}
      />
    </Stack>
  );
}

/**
 * Inventory Routes Layout (Root Level) 📦
 * 
 * Stack navigator for the root-level /inventory route.
 * This handles URLs like /inventory and /inventory/:id
 * that are accessed directly (e.g., from bookmarks or external links).
 */

import { Stack } from 'expo-router';

export default function InventoryRootLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: false,
        animation: 'slide_from_right',
      }}
    >
      <Stack.Screen
        name="index"
        options={{
          title: 'Pantry',
        }}
      />
      <Stack.Screen
        name="[id]"
        options={{
          title: 'Item Details',
          headerShown: true,
        }}
      />
    </Stack>
  );
}

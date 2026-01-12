/**
 * Inventory Routes Layout 📦
 * 
 * Stack navigator for the inventory/pantry module.
 */

import { Stack } from 'expo-router';

export default function InventoryLayout() {
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
          title: 'Pantry',
          headerLargeTitle: true,
        }}
      />
      <Stack.Screen
        name="scan-result"
        options={{
          title: 'Confirm Items',
          presentation: 'modal',
        }}
      />
    </Stack>
  );
}

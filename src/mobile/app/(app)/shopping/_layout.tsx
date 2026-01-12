/**
 * Shopping Routes Layout 🛒
 * 
 * Stack navigator for the shopping module.
 */

import { Stack } from 'expo-router';

export default function ShoppingLayout() {
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
          title: 'Shopping List',
          headerLargeTitle: true,
        }}
      />
    </Stack>
  );
}

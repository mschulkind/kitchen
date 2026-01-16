import { Stack } from 'expo-router';

export default function AppLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: false,
        animation: 'slide_from_right',
      }}
    >
      <Stack.Screen name="index" options={{ title: 'Hub' }} />
      <Stack.Screen name="inventory" options={{ title: 'Pantry', headerShown: false }} />
      <Stack.Screen name="recipes" options={{ title: 'Recipes', headerShown: false }} />
      <Stack.Screen name="planner" options={{ title: 'Meal Plan', headerShown: false }} />
      <Stack.Screen name="shopping" options={{ title: 'Shopping List', headerShown: false }} />
      <Stack.Screen name="settings" options={{ title: 'Settings', headerShown: true }} />
    </Stack>
  );
}

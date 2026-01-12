/**
 * Planner Routes Layout 📅
 * 
 * Stack navigator for the planner module.
 * Includes calendar view and new plan generator.
 */

import { Stack } from 'expo-router';

export default function PlannerLayout() {
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
          title: 'Meal Planner',
          headerLargeTitle: true,
        }}
      />
      <Stack.Screen
        name="new"
        options={{
          title: 'Create New Plan',
          presentation: 'modal',
        }}
      />
      <Stack.Screen
        name="preview"
        options={{
          title: 'Choose Your Adventure',
          presentation: 'modal',
        }}
      />
    </Stack>
  );
}

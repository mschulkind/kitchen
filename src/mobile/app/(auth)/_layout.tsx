import { Stack } from 'expo-router';

/**
 * Auth Layout - Public routes 🔓
 * 
 * Handles unauthenticated screens like landing and login.
 */
export default function AuthLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: false,
        animation: 'fade',
      }}
    />
  );
}

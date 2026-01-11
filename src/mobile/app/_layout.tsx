/**
 * Root Layout 🏠
 * 
 * Sets up global providers: Tamagui, TanStack Query, Auth.
 * This wraps the entire application.
 */

import { useEffect } from 'react';
import { useColorScheme } from 'react-native';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { TamaguiProvider, Theme } from 'tamagui';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import config from '../tamagui.config';

// Create a client for TanStack Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 2,
    },
  },
});

export default function RootLayout() {
  const colorScheme = useColorScheme();

  return (
    <QueryClientProvider client={queryClient}>
      <TamaguiProvider config={config}>
        <Theme name={colorScheme === 'dark' ? 'dark' : 'light'}>
          <StatusBar style="auto" />
          <Stack
            screenOptions={{
              headerShown: true,
              headerStyle: {
                backgroundColor: colorScheme === 'dark' ? '#1a1a1a' : '#ffffff',
              },
              headerTintColor: colorScheme === 'dark' ? '#ffffff' : '#000000',
            }}
          >
            <Stack.Screen
              name="(tabs)"
              options={{ headerShown: false }}
            />
          </Stack>
        </Theme>
      </TamaguiProvider>
    </QueryClientProvider>
  );
}

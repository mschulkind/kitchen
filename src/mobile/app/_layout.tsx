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
import { TamaguiProvider, Theme, PortalProvider } from 'tamagui';
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
  
  // Force light mode for now to ensure consistency across web/mobile 
  // until dark mode is fully optimized
  const forcedTheme: 'light' | 'dark' = 'light'; 

  // Check if we're on web and force the class on html element
  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.documentElement.classList.remove('t_dark');
      document.documentElement.classList.add('t_light');
      document.documentElement.style.backgroundColor = '#ffffff';

      // Ensure root has height for React Native Web
      document.documentElement.style.height = '100%';
      document.body.style.height = '100%';
      const root = document.getElementById('root');
      if (root) {
        root.style.height = '100%';
        root.style.display = 'flex';
        root.style.flex = '1';
      }
    }
  }, []);

  const themeColors = {
    light: {
      headerBg: '#ffffff',
      headerTint: '#000000',
      contentBg: '#ffffff',
    },
    dark: {
      headerBg: '#1a1a1a',
      headerTint: '#ffffff',
      contentBg: '#000000',
    },
  }[forcedTheme];

  return (
    <QueryClientProvider client={queryClient}>
      <TamaguiProvider config={config}>
        <Theme name={forcedTheme}>
          <PortalProvider shouldAddRootHost>
            <StatusBar style="auto" />
            <Stack
              screenOptions={{
                headerShown: true,
                headerStyle: {
                  backgroundColor: themeColors.headerBg,
                },
                headerTintColor: themeColors.headerTint,
                contentStyle: {
                  backgroundColor: themeColors.contentBg,
                },
              }}
            >
              <Stack.Screen
                name="(auth)"
                options={{ headerShown: false }}
              />
              <Stack.Screen
                name="(app)"
                options={{ headerShown: false }}
              />
            </Stack>
          </PortalProvider>
        </Theme>
      </TamaguiProvider>
    </QueryClientProvider>
  );
}

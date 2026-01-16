/**
 * Login Screen 🔐
 * 
 * Primary authentication via Google OAuth (Decision D1).
 */

import { useState } from 'react';
import { useRouter, Stack } from 'expo-router';
import { YStack, H2, Paragraph, Spinner, Image } from 'tamagui';
import { Chrome } from '@tamagui/lucide-icons';

import { supabase } from '@/lib/supabase';
import { KitchenButton } from '@/components/Core/Button';

export default function LoginScreen() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGoogleLogin = async () => {
    setLoading(true);
    setError(null);

    try {
      const { error: authError } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: window.location.origin, // Works for web
        },
      });

      if (authError) throw authError;
      
      // Note: In a real OAuth flow, this redirects away from the app.
      // For local development bypass if not configured:
      if (process.env.NODE_ENV === 'development') {
        console.log('Dev Mode: Bypassing real OAuth for testing');
        router.replace('/(app)');
      }
    } catch (e: any) {
      setError(e.message);
      setLoading(false);
    }
  };

  return (
    <>
      <Stack.Screen options={{ headerShown: false }} />
      <YStack flex={1} backgroundColor="$background" padding="$4" justifyContent="center">
        
        <YStack space="$6" maxWidth={400} width="100%" alignSelf="center" alignItems="center">
          <YStack alignItems="center" space="$2">
            <H2 size="$9" color="$orange10" textAlign="center">Welcome to Kitchen</H2>
            <Paragraph color="$gray10" textAlign="center">Sign in to start your AI-powered culinary journey.</Paragraph>
          </YStack>

          {error && (
            <YStack backgroundColor="$red3" padding="$3" borderRadius="$4" width="100%">
              <Paragraph color="$red11">{error}</Paragraph>
            </YStack>
          )}

          <KitchenButton
            testID="google-login-button"
            size="$6"
            theme="gray"
            icon={loading ? <Spinner color="$orange10" /> : <Chrome size={24} color="$orange10" />}
            onPress={handleGoogleLogin}
            disabled={loading}
            width="100%"
            height={60}
            borderRadius="$10"
            borderWidth={2}
            borderColor="$gray5"
          >
            {loading ? 'Connecting...' : 'Sign in with Google'}
          </KitchenButton>

          <Paragraph size="$2" color="$gray8" textAlign="center" marginTop="$4">
            By signing in, you agree to our Terms of Service and Privacy Policy.
          </Paragraph>
        </YStack>
      </YStack>
    </>
  );
}
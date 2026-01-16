/**
 * Login Screen 🔐
 * 
 * Supabase Email/Password authentication.
 */

import { useState } from 'react';
import { useRouter, Stack } from 'expo-router';
import { YStack, H2, Input, Button, Paragraph, Spinner, XStack } from 'tamagui';
import { Mail, Lock, LogIn } from '@tamagui/lucide-icons';

import { supabase } from '@/lib/supabase';
import { KitchenButton } from '@/components/Core/Button';

export default function LoginScreen() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async () => {
    if (!email || !password) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);
    setError(null);

    const { error: authError } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (authError) {
      setError(authError.message);
      setLoading(false);
    } else {
      // Auth state listener in _layout will handle redirect
      // But we can force it just in case
      router.replace('/(app)');
    }
  };

  return (
    <>
      <Stack.Screen options={{ headerShown: false }} />
      <YStack flex={1} backgroundColor="$background" padding="$4" justifyContent="center">
        
        <YStack space="$4" maxWidth={400} width="100%" alignSelf="center">
          <YStack marginBottom="$4">
            <H2 size="$9" color="$orange10">Welcome Back</H2>
            <Paragraph color="$gray10">Sign in to continue cooking.</Paragraph>
          </YStack>

          {error && (
            <YStack backgroundColor="$red3" padding="$3" borderRadius="$4">
              <Paragraph color="$red11">{error}</Paragraph>
            </YStack>
          )}

          <YStack space="$3">
            <XStack alignItems="center" backgroundColor="$gray3" borderRadius="$4" paddingHorizontal="$3">
              <Mail size={20} color="$gray9" />
              <Input
                flex={1}
                size="$4"
                placeholder="Email"
                value={email}
                onChangeText={setEmail}
                autoCapitalize="none"
                keyboardType="email-address"
                borderWidth={0}
                backgroundColor="transparent"
              />
            </XStack>

            <XStack alignItems="center" backgroundColor="$gray3" borderRadius="$4" paddingHorizontal="$3">
              <Lock size={20} color="$gray9" />
              <Input
                flex={1}
                size="$4"
                placeholder="Password"
                value={password}
                onChangeText={setPassword}
                secureTextEntry
                borderWidth={0}
                backgroundColor="transparent"
              />
            </XStack>
          </YStack>

          <KitchenButton
            size="$5"
            theme="orange"
            icon={loading ? <Spinner color="white" /> : <LogIn size={20} />}
            onPress={handleLogin}
            disabled={loading}
            marginTop="$2"
          >
            {loading ? 'Signing In...' : 'Sign In'}
          </KitchenButton>

          <Button
            chromeless
            size="$3"
            color="$gray10"
            onPress={() => router.push('/(auth)/signup')}
            marginTop="$2"
          >
            Don't have an account? Sign Up
          </Button>
        </YStack>
      </YStack>
    </>
  );
}

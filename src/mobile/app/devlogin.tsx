/**
 * Dev Login Route 🛠️
 * 
 * A backdoor login for development and automation.
 * STRICTLY DISABLED IN PRODUCTION.
 */

import { useState } from 'react';
import { Redirect, useRouter } from 'expo-router';
import { YStack, H1, Paragraph, Input, Button, Spinner, XStack, Label } from 'tamagui';
import { Lock, AlertTriangle } from '@tamagui/lucide-icons';
import { supabase } from '@/lib/supabase';

export default function DevLoginScreen() {
  const router = useRouter();
  const [email, setEmail] = useState('admin@kitchen.local');
  const [password, setPassword] = useState('admin123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [debugInfo, setDebugInfo] = useState<string>('');

  // 🛡️ SECURITY: Fail-safe for production
  if (process.env.NODE_ENV !== 'development') {
    return <Redirect href="/" />;
  }

  const testConnection = async () => {
    try {
      // @ts-ignore - accessing internal property for debugging
      const url = supabase.supabaseUrl;
      setDebugInfo(`Checking connection to: ${url}...`);
      
      const res = await fetch(`${url}/auth/v1/health`, { method: 'GET' }).catch(e => {
        throw new Error(`Fetch failed: ${e.message}`);
      });
      
      setDebugInfo(`Connection OK: ${url} (Status: ${res.status})`);
      return true;
    } catch (e: any) {
      setDebugInfo(`Connection Failed: ${e.message}`);
      return false;
    }
  };

  const handleLogin = async () => {
    setLoading(true);
    setError(null);
    setDebugInfo('Authenticating...');

    try {
      // Test connection first
      const isConnected = await testConnection();
      if (!isConnected) {
        throw new Error('Could not connect to Supabase. See debug info.');
      }

      // Add a timeout to the login request
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Login timed out (10s)')), 10000)
      );

      const loginPromise = supabase.auth.signInWithPassword({
        email,
        password,
      });

      const { data, error: authError } = await Promise.race([loginPromise, timeoutPromise]) as any;

      if (authError) throw authError;

      setDebugInfo('Login successful! Redirecting...');
      // Redirect to app on success
      router.replace('/(app)');
    } catch (e: any) {
      setError(e.message);
      setLoading(false);
    }
  };

  return (
    <YStack flex={1} backgroundColor="$background" padding="$6" justifyContent="center" space="$4">
      
      {/* Warning Header */}
      <YStack alignItems="center" space="$2" marginBottom="$4">
        <YStack 
          width={80} 
          height={80} 
          backgroundColor="$red3" 
          borderRadius="$10" 
          justifyContent="center" 
          alignItems="center"
        >
          <Lock size={40} color="$red10" />
        </YStack>
        <H1 size="$8" color="$red10">Dev Access</H1>
        <XStack alignItems="center" space="$2" backgroundColor="$yellow3" padding="$2" borderRadius="$4">
          <AlertTriangle size={16} color="$yellow11" />
          <Paragraph size="$3" color="$yellow11" fontWeight="bold">
            DEVELOPMENT ONLY
          </Paragraph>
        </XStack>
      </YStack>

      {/* Login Form */}
      <YStack space="$4">
        <YStack space="$2">
          <Label htmlFor="email">Service Account Email</Label>
          <Input
            id="email"
            value={email}
            onChangeText={setEmail}
            autoCapitalize="none"
            keyboardType="email-address"
          />
        </YStack>

        <YStack space="$2">
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            value={password}
            onChangeText={setPassword}
            secureTextEntry
          />
        </YStack>

        {error && (
          <YStack backgroundColor="$red3" padding="$3" borderRadius="$4">
            <Paragraph color="$red11">{error}</Paragraph>
          </YStack>
        )}

        {debugInfo ? (
          <YStack backgroundColor="$gray3" padding="$2" borderRadius="$4" marginBottom="$2">
            <Paragraph size="$2" color="$gray11" fontFamily="$mono">{debugInfo}</Paragraph>
          </YStack>
        ) : null}

        <Button
          testID="dev-login-button"
          theme="red"
          size="$5"
          onPress={handleLogin}
          disabled={loading}
          icon={loading ? <Spinner /> : undefined}
        >
          {loading ? 'Authenticating...' : 'Authorize Service Account'}
        </Button>
      </YStack>

      <Paragraph size="$2" color="$gray8" textAlign="center" marginTop="$4">
        This route is disabled in production builds.
      </Paragraph>
    </YStack>
  );
}

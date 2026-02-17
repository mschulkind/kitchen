/**
 * Landing Page 🛬
 * 
 * First screen users see. Prompts for Google Sign In.
 */

import { useState } from 'react';
import { useRouter } from 'expo-router';
import { YStack, H1, H2, Paragraph, XStack, Spinner } from 'tamagui';
import { ChefHat, Chrome } from '@tamagui/lucide-icons';

import { supabase } from '@/lib/supabase';
import { KitchenButton } from '@/components/Core/Button';

export default function LandingScreen() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGoogleLogin = async () => {
    setLoading(true);
    setError(null);

    try {
      // For local development bypass if not configured:
      if (process.env.NODE_ENV === 'development' && !process.env.EXPO_PUBLIC_USE_REAL_OAUTH) {
        console.log('Dev Mode: Bypassing real OAuth for testing');
        // Use dev login credentials to create a real session that persists
        const { error: signInError } = await supabase.auth.signInWithPassword({
          email: 'admin@kitchen.local',
          password: 'admin123',
        });
        if (signInError) {
          console.warn('Dev auto-login failed, routing anyway:', signInError.message);
        }
        router.replace('/(app)');
        return;
      }

      const { error: authError } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: typeof window !== 'undefined' ? window.location.origin : undefined,
        },
      });

      if (authError) throw authError;
    } catch (e: any) {
      setError(e.message);
      setLoading(false);
    }
  };

  return (
    <YStack flex={1} backgroundColor="$background" justifyContent="space-between" padding="$6" paddingTop="$10" testID="landing-screen" maxWidth={500} width="100%" alignSelf="center">
      
      {/* Hero Section */}
      <YStack space="$4" alignItems="center">
        <YStack 
          width={120} 
          height={120} 
          backgroundColor="$orange5" 
          borderRadius="$10" 
          justifyContent="center" 
          alignItems="center"
          elevation="$4"
        >
          <ChefHat size={60} color="$orange10" />
        </YStack>
        
        <H1 size="$10" color="$orange10">Kitchen</H1>
        <Paragraph size="$5" color="$gray11" textAlign="center" maxWidth={300}>
          Your AI-powered sous chef, inventory manager, and meal planner.
        </Paragraph>
      </YStack>

      {/* Value Props */}
      <YStack space="$5">
        <FeatureItem 
          icon="🥬" 
          title="Smart Pantry" 
          text="Track ingredients & reduce waste." 
        />
        <FeatureItem 
          icon="🍳" 
          title="AI Recipes" 
          text="Cook what you have, step-by-step." 
        />
        <FeatureItem 
          icon="🛒" 
          title="Auto Shopping" 
          text="Lists that build themselves." 
        />
      </YStack>

      {/* Actions */}
      <YStack space="$3" marginBottom="$6">
        {error && (
          <YStack backgroundColor="$red3" padding="$3" borderRadius="$4" marginBottom="$2">
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

        {/* Dev Login Backdoor */}
        {process.env.NODE_ENV === 'development' && (
          <KitchenButton
            size="$3"
            chromeless
            onPress={() => router.push('/devlogin')}
            marginTop="$2"
            opacity={0.5}
          >
            🛠️ Dev Login
          </KitchenButton>
        )}
      </YStack>
    </YStack>
  );
}

function FeatureItem({ icon, title, text }: { icon: string; title: string; text: string }) {
  return (
    <XStack space="$4" alignItems="center">
      <YStack width={40} alignItems="center">
        <H2 size="$6">{icon}</H2>
      </YStack>
      <YStack>
        <H2 size="$4" fontWeight="bold" color="$gray12">{title}</H2>
        <Paragraph size="$3" color="$gray10">{text}</Paragraph>
      </YStack>
    </XStack>
  );
}
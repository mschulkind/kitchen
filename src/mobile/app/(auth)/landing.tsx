```tsx
/**
 * Landing Page 🛬
 * 
 * First screen users see. Prompts for login.
 */

import { Link, useRouter } from 'expo-router';
import { YStack, H1, H2, Paragraph, Button, XStack, Image } from 'tamagui';
import { ChefHat, ArrowRight } from '@tamagui/lucide-icons';
import { supabase } from '@/lib/supabase';

export default function LandingScreen() {
  const router = useRouter();

  const handleMockLogin = async () => {
    // For Phase 2, we just bypass auth to the app hub
    // In real implementation, this would trigger Supabase Auth
    router.replace('/(app)');
  };

  return (
    <YStack flex={1} backgroundColor="$background" justifyContent="space-between" padding="$6" paddingTop="$10">
      
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
        <Button 
          size="$6" 
          theme="orange" 
          iconAfter={<ArrowRight size={20} />}
          onPress={handleMockLogin}
          fontWeight="bold"
        >
          Get Started
        </Button>
        
        <Button size="$4" chromeless color="$gray10">
          Already have an account? Sign In
        </Button>
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
```
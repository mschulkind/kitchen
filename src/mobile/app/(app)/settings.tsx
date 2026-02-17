/**
 * Settings Screen ⚙️
 * 
 * App configuration and user preferences.
 */

import { useState, useEffect } from 'react';
import { YStack, XStack, Text, H1, H2, Card, Switch, Button, Separator, Input } from 'tamagui';
import { User, Home, Bell, Moon, LogOut, Store } from '@tamagui/lucide-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';

import { supabase } from '@/lib/supabase';

const STORE_KEY = 'preferred_store';

export default function SettingsScreen() {
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [preferredStore, setPreferredStore] = useState('');
  const [storeSaved, setStoreSaved] = useState(false);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setUserEmail(data.session?.user?.email ?? null);
    });
    AsyncStorage.getItem(STORE_KEY).then((val) => {
      if (val) setPreferredStore(val);
    });
  }, []);

  const displayName = userEmail || 'Guest User';
  const isSignedIn = !!userEmail;

  return (
    <YStack flex={1} padding="$4" backgroundColor="$background">
      <H1 marginBottom="$4">Settings ⚙️</H1>

      {/* Account Section */}
      <Card elevate padding="$4" marginBottom="$4">
        <XStack alignItems="center" space="$3">
          <YStack
            width={60}
            height={60}
            borderRadius={30}
            backgroundColor="$blue5"
            justifyContent="center"
            alignItems="center"
          >
            <User size={30} color="#2563eb" />
          </YStack>
          <YStack flex={1}>
            <Text fontSize="$5" fontWeight="600">{displayName}</Text>
            <Text color="$gray10" fontSize="$3">
              {isSignedIn ? 'Signed in' : 'Sign in for sync'}
            </Text>
          </YStack>
          {!isSignedIn && <Button size="$3" theme="blue">Sign In</Button>}
        </XStack>
      </Card>

      {/* Household Section */}
      <H2 marginBottom="$2">Household</H2>
      <Card elevate padding="$4" marginBottom="$4">
        <XStack alignItems="center" space="$3">
          <Home size={24} color="#6b7280" />
          <YStack flex={1}>
            <Text fontSize="$4">My Kitchen</Text>
            <Text color="$gray10" fontSize="$2">1 member</Text>
          </YStack>
          <Button size="$3" chromeless>Manage</Button>
        </XStack>
      </Card>

      {/* Preferences */}
      <H2 marginBottom="$2">Preferences</H2>
      <Card elevate padding="$4" marginBottom="$4">
        <YStack space="$4">
          <XStack alignItems="center" justifyContent="space-between">
            <XStack alignItems="center" space="$3">
              <Bell size={20} color="#6b7280" />
              <Text>Expiry Notifications</Text>
            </XStack>
            <Switch size="$3" defaultChecked />
          </XStack>
          
          <Separator />
          
          <XStack alignItems="center" justifyContent="space-between">
            <XStack alignItems="center" space="$3">
              <Moon size={20} color="#6b7280" />
              <Text>Dark Mode</Text>
            </XStack>
            <Switch size="$3" />
          </XStack>
        </YStack>
      </Card>

      {/* Preferred Store */}
      <H2 marginBottom="$2">Preferred Store 🏪</H2>
      <Card elevate padding="$4" marginBottom="$4">
        <YStack space="$3">
          <XStack alignItems="center" space="$3">
            <Store size={20} color="#6b7280" />
            <Text>Your go-to grocery store</Text>
          </XStack>
          <Input
            testID="preferred-store-input"
            placeholder="e.g. Trader Joe's, Costco..."
            value={preferredStore}
            onChangeText={(val: string) => {
              setPreferredStore(val);
              setStoreSaved(false);
            }}
          />
          <Button
            testID="save-store-button"
            size="$3"
            theme="green"
            onPress={async () => {
              await AsyncStorage.setItem(STORE_KEY, preferredStore);
              setStoreSaved(true);
            }}
          >
            {storeSaved ? '✅ Saved!' : 'Save Store'}
          </Button>
        </YStack>
      </Card>

      {/* About */}
      <Card elevate padding="$4">
        <YStack space="$2">
          <Text color="$gray10" fontSize="$2">Kitchen App v0.1.0</Text>
        </YStack>
      </Card>
    </YStack>
  );
}

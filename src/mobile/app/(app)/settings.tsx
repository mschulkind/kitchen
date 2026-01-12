/**
 * Settings Screen ⚙️
 * 
 * App configuration and user preferences.
 */

import { YStack, XStack, Text, H1, H2, Card, Switch, Button, Separator } from 'tamagui';
import { User, Home, Bell, Moon, LogOut } from '@tamagui/lucide-icons';

export default function SettingsScreen() {
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
            <Text fontSize="$5" fontWeight="600">Guest User</Text>
            <Text color="$gray10" fontSize="$3">Sign in for sync</Text>
          </YStack>
          <Button size="$3" theme="blue">Sign In</Button>
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

      {/* About */}
      <Card elevate padding="$4">
        <YStack space="$2">
          <Text color="$gray10" fontSize="$2">Kitchen App v0.1.0</Text>
          <Text color="$gray10" fontSize="$2">Phase 1: Foundation & Inventory</Text>
        </YStack>
      </Card>
    </YStack>
  );
}

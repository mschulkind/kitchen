/**
 * The Hub Dashboard 🏠
 * 
 * Central navigation point for the authenticated app.
 * Replaces the old tab-based layout with a immersive grid.
 */

import { Link, useRouter } from 'expo-router';
import { ScrollView } from 'react-native';
import { YStack, XStack, H2, H3, Paragraph, Card, Button, Avatar } from 'tamagui';
import { 
  ChefHat, 
  ShoppingCart, 
  Calendar, 
  Package, 
  Settings, 
  LogOut 
} from '@tamagui/lucide-icons';

export default function HubScreen() {
  const router = useRouter();

  return (
    <YStack flex={1} backgroundColor="$background">
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 40 }}>
        
        {/* Header */}
        <XStack justifyContent="space-between" alignItems="center" marginBottom="$6" marginTop="$8">
          <YStack>
            <Paragraph color="$gray10" fontSize="$3">Good Evening,</Paragraph>
            <H2 color="$gray12">Chef Matt</H2>
          </YStack>
          <Avatar circular size="$4">
            <Avatar.Image src="https://i.pravatar.cc/150?u=kitchen" />
            <Avatar.Fallback backgroundColor="$gray5" />
          </Avatar>
        </XStack>

        {/* Hero Widget: Tonight's Plan */}
        <Card elevate size="$4" bordered animation="bouncy" pressStyle={{ scale: 0.98 }} marginBottom="$6">
          <Card.Header padded>
            <XStack justifyContent="space-between">
              <H3>Tonight's Dinner</H3>
              <Calendar size={20} color="$green10" />
            </XStack>
            <Paragraph theme="alt2" marginTop="$2">Chicken Tikka Masala</Paragraph>
            <Paragraph fontSize="$3" color="$gray10">Prep: 20m • Cook: 40m</Paragraph>
          </Card.Header>
          <Card.Footer padded>
            <Button theme="green" icon={<ChefHat size={16} />}>Start Cooking</Button>
          </Card.Footer>
        </Card>

        {/* Dashboard Grid */}
        <H3 marginBottom="$4" color="$gray11">Modules</H3>
        <YStack space="$4">
          
          <XStack space="$4">
            <HubCard 
              title="Recipes" 
              subtitle="Browse & Cook"
              icon={<ChefHat size={32} color="#f97316" />}
              color="$orange2"
              href="/(app)/recipes"
            />
            <HubCard 
              title="Pantry" 
              subtitle="Manage Stock"
              icon={<Package size={32} color="#3b82f6" />}
              color="$blue2"
              href="/(app)/inventory"
            />
          </XStack>

          <XStack space="$4">
            <HubCard 
              title="Planner" 
              subtitle="Week Layout"
              icon={<Calendar size={32} color="#22c55e" />}
              color="$green2"
              href="/(app)/planner"
            />
            <HubCard 
              title="Shopping" 
              subtitle="Grocery List"
              icon={<ShoppingCart size={32} color="#eab308" />}
              color="$yellow2"
              href="/(app)/shopping"
            />
          </XStack>

        </YStack>

        {/* Utility Links */}
        <YStack marginTop="$8" space="$2">
          <Button 
            chromeless 
            icon={<Settings size={18} />} 
            color="$gray10" 
            justifyContent="flex-start"
            onPress={() => router.push('/(app)/settings')}
          >
            Settings
          </Button>
          <Button 
            chromeless 
            icon={<LogOut size={18} />} 
            color="$red10" 
            justifyContent="flex-start"
            onPress={() => router.replace('/(auth)/landing')}
          >
            Sign Out
          </Button>
        </YStack>

      </ScrollView>
    </YStack>
  );
}

function HubCard({ 
  title, 
  subtitle, 
  icon, 
  color, 
  href 
}: { 
  title: string; 
  subtitle: string; 
  icon: React.ReactNode; 
  color: string; 
  href: string;
}) {
  const router = useRouter();
  
  return (
    <Card 
      flex={1} 
      height={140} 
      backgroundColor={color} 
      borderRadius="$6"
      pressStyle={{ scale: 0.96, opacity: 0.9 }}
      animations="bouncy"
      onPress={() => router.push(href)}
      justifyContent="center"
      alignItems="center"
      elevate
    >
      <YStack alignItems="center" space="$2">
        {icon}
        <H3 fontSize="$5" color="$gray12">{title}</H3>
        <Paragraph fontSize="$2" color="$gray11">{subtitle}</Paragraph>
      </YStack>
    </Card>
  );
}

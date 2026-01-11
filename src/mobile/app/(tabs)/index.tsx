/**
 * Home Screen 🏠
 * 
 * Dashboard with quick stats and actions.
 */

import { YStack, XStack, Text, H1, H2, Card, Button, Paragraph } from 'tamagui';
import { Link } from 'expo-router';
import { Package, Calendar, ShoppingCart, AlertTriangle } from '@tamagui/lucide-icons';

export default function HomeScreen() {
  return (
    <YStack flex={1} padding="$4" space="$4" backgroundColor="$background">
      <H1>Kitchen 🍳</H1>
      <Paragraph color="$gray10">Your AI-powered meal planning assistant</Paragraph>

      {/* Quick Stats */}
      <XStack space="$3" flexWrap="wrap">
        <StatCard
          icon={<Package size={24} color="#2563eb" />}
          label="Pantry Items"
          value="--"
        />
        <StatCard
          icon={<Calendar size={24} color="#16a34a" />}
          label="Meals Planned"
          value="--"
        />
        <StatCard
          icon={<ShoppingCart size={24} color="#f59e0b" />}
          label="To Buy"
          value="--"
        />
        <StatCard
          icon={<AlertTriangle size={24} color="#dc2626" />}
          label="Expiring Soon"
          value="--"
        />
      </XStack>

      {/* Quick Actions */}
      <H2 marginTop="$4">Quick Actions</H2>
      <YStack space="$3">
        <Link href="/inventory" asChild>
          <Button size="$5" theme="blue" icon={<Package size={20} />}>
            Manage Pantry
          </Button>
        </Link>
        <Link href="/planner" asChild>
          <Button size="$5" theme="green" icon={<Calendar size={20} />}>
            Plan Meals
          </Button>
        </Link>
        <Link href="/shopping" asChild>
          <Button size="$5" theme="orange" icon={<ShoppingCart size={20} />}>
            Shopping List
          </Button>
        </Link>
      </YStack>
    </YStack>
  );
}

function StatCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <Card
      elevate
      size="$4"
      width={150}
      height={100}
      padding="$3"
      animation="bouncy"
      pressStyle={{ scale: 0.97 }}
    >
      <YStack flex={1} justifyContent="space-between">
        {icon}
        <Text fontSize="$8" fontWeight="bold">
          {value}
        </Text>
        <Text fontSize="$2" color="$gray10">
          {label}
        </Text>
      </YStack>
    </Card>
  );
}

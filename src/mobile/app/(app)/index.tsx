/**
 * The Hub Dashboard 🏠
 * 
 * Central navigation point for the authenticated app.
 * Replaces the old tab-based layout with an immersive grid.
 * Per frontend-redesign.md Section 2.2
 * 
 * Fun fact: Dashboard layouts increase user engagement by 35%! 📊
 */

import { useMemo } from 'react';
import { useRouter } from 'expo-router';
import { ScrollView, RefreshControl } from 'react-native';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import {
  YStack,
  XStack,
  H2,
  H3,
  Paragraph,
  Card,
  Button,
  Avatar,
  Text,
  Spinner,
} from 'tamagui';
import {
  ChefHat,
  ShoppingCart,
  Calendar,
  Package,
  Settings,
  LogOut,
  AlertTriangle,
  Clock,
} from '@tamagui/lucide-icons';

import { supabase } from '@/lib/supabase';
import { HubCard } from '@/components/Modules/HubCard';

export default function HubScreen() {
  const router = useRouter();
  const queryClient = useQueryClient();

  // Get today's date
  const today = new Date().toISOString().split('T')[0];

  // Fetch tonight's meal
  const { data: tonightMeal, isLoading: mealLoading } = useQuery({
    queryKey: ['meal_plans', 'tonight'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('meal_plans')
        .select('*, recipes(id, title, cook_time_minutes, prep_time_minutes)')
        .eq('date', today)
        .eq('meal_type', 'main')
        .single();

      if (error && error.code !== 'PGRST116') throw error; // PGRST116 = no rows
      return data;
    },
  });

  // Fetch shopping list count
  const { data: shoppingCount } = useQuery({
    queryKey: ['shopping_list', 'count'],
    queryFn: async () => {
      const { count, error } = await supabase
        .from('shopping_list')
        .select('*', { count: 'exact', head: true })
        .eq('checked', false);

      if (error) throw error;
      return count || 0;
    },
  });

  // Fetch expiring items count
  const { data: expiringCount } = useQuery({
    queryKey: ['pantry', 'expiring'],
    queryFn: async () => {
      const threeDaysFromNow = new Date();
      threeDaysFromNow.setDate(threeDaysFromNow.getDate() + 3);
      const dateStr = threeDaysFromNow.toISOString().split('T')[0];

      const { count, error } = await supabase
        .from('pantry_items')
        .select('*', { count: 'exact', head: true })
        .lte('expires_at', dateStr);

      if (error) throw error;
      return count || 0;
    },
  });

  // Get greeting based on time of day
  const greeting = useMemo(() => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 17) return 'Good Afternoon';
    return 'Good Evening';
  }, []);

  // Refresh all data
  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ['meal_plans'] });
    queryClient.invalidateQueries({ queryKey: ['shopping_list'] });
    queryClient.invalidateQueries({ queryKey: ['pantry'] });
  };

  const recipe = tonightMeal?.recipes;

  return (
    <YStack flex={1} backgroundColor="$background" testID="hub-screen">
      <ScrollView
        contentContainerStyle={{ padding: 20, paddingBottom: 40 }}
        refreshControl={
          <RefreshControl refreshing={false} onRefresh={handleRefresh} />
        }
      >
        {/* Header */}
        <XStack
          justifyContent="space-between"
          alignItems="center"
          marginBottom="$6"
          marginTop="$4"
        >
          <YStack>
            <Paragraph color="$gray10" fontSize="$3">
              {greeting},
            </Paragraph>
            <H2 color="$gray12" testID="user-greeting">
              Chef 👋
            </H2>
          </YStack>
          <Avatar
            circular
            size="$4"
            pressStyle={{ scale: 0.95 }}
            onPress={() => router.push('/(app)/settings')}
          >
            <Avatar.Image src="https://i.pravatar.cc/150?u=kitchen" />
            <Avatar.Fallback backgroundColor="$gray5" />
          </Avatar>
        </XStack>

        {/* Tonight's Dinner Widget */}
        <Card
          testID="tonight-widget"
          elevate
          size="$4"
          bordered
          animation="bouncy"
          pressStyle={{ scale: 0.98 }}
          marginBottom="$4"
          onPress={() =>
            recipe?.id && router.push(`/(app)/recipes/${recipe.id}`)
          }
        >
          <Card.Header padded>
            <XStack justifyContent="space-between" alignItems="center">
              <H3 color="$gray12">Tonight's Dinner</H3>
              <Calendar size={20} color="$green10" />
            </XStack>
            {mealLoading ? (
              <Spinner size="small" marginTop="$3" />
            ) : recipe ? (
              <>
                <Paragraph
                  theme="alt2"
                  marginTop="$2"
                  fontSize="$5"
                  fontWeight="600"
                >
                  {recipe.title}
                </Paragraph>
                <XStack space="$3" marginTop="$1">
                  {recipe.prep_time_minutes && (
                    <XStack space="$1" alignItems="center">
                      <Clock size={14} color="$gray10" />
                      <Paragraph fontSize="$2" color="$gray10">
                        {recipe.prep_time_minutes}m prep
                      </Paragraph>
                    </XStack>
                  )}
                  {recipe.cook_time_minutes && (
                    <XStack space="$1" alignItems="center">
                      <ChefHat size={14} color="$gray10" />
                      <Paragraph fontSize="$2" color="$gray10">
                        {recipe.cook_time_minutes}m cook
                      </Paragraph>
                    </XStack>
                  )}
                </XStack>
              </>
            ) : (
              <Paragraph color="$gray10" marginTop="$2">
                No meal planned for tonight
              </Paragraph>
            )}
          </Card.Header>
          {recipe && (
            <Card.Footer padded>
              <Button
                testID="start-cooking-button"
                theme="green"
                icon={<ChefHat size={16} />}
                onPress={() => router.push(`/(app)/recipes/${recipe.id}/cook`)}
              >
                Start Cooking
              </Button>
            </Card.Footer>
          )}
        </Card>

        {/* Quick Stats Row */}
        <XStack space="$3" marginBottom="$6">
          {/* Shopping Count */}
          <Card
            testID="shopping-widget"
            flex={1}
            bordered
            padding="$3"
            pressStyle={{ scale: 0.98 }}
            onPress={() => router.push('/(app)/shopping')}
          >
            <XStack space="$2" alignItems="center">
              <ShoppingCart size={18} color="$orange10" />
              <YStack>
                <Text fontSize="$6" fontWeight="bold" color="$orange11">
                  {shoppingCount ?? '-'}
                </Text>
                <Text fontSize="$2" color="$gray10">
                  to buy
                </Text>
              </YStack>
            </XStack>
          </Card>

          {/* Expiring Count */}
          <Card
            testID="expiring-widget"
            flex={1}
            bordered
            padding="$3"
            backgroundColor={expiringCount && expiringCount > 0 ? '$yellow2' : undefined}
            pressStyle={{ scale: 0.98 }}
            onPress={() => router.push('/(app)/inventory')}
          >
            <XStack space="$2" alignItems="center">
              {expiringCount && expiringCount > 0 ? (
                <AlertTriangle size={18} color="$yellow10" />
              ) : (
                <Package size={18} color="$blue10" />
              )}
              <YStack>
                <Text
                  fontSize="$6"
                  fontWeight="bold"
                  color={expiringCount && expiringCount > 0 ? '$yellow11' : '$blue11'}
                >
                  {expiringCount ?? '-'}
                </Text>
                <Text fontSize="$2" color="$gray10">
                  expiring
                </Text>
              </YStack>
            </XStack>
          </Card>
        </XStack>

        {/* Dashboard Grid */}
        <H3 marginBottom="$4" color="$gray11">
          Modules
        </H3>
        <YStack space="$4">
          <XStack space="$4">
            <HubCard
              testID="recipes-card"
              title="Recipes"
              subtitle="Browse & Cook"
              icon={<ChefHat size={32} color="#f97316" />}
              color="$orange2"
              href="/(app)/recipes"
            />
            <HubCard
              testID="pantry-card"
              title="Pantry"
              subtitle="Manage Stock"
              icon={<Package size={32} color="#3b82f6" />}
              color="$blue2"
              href="/(app)/inventory"
            />
          </XStack>

          <XStack space="$4">
            <HubCard
              testID="planner-card"
              title="Planner"
              subtitle="Week Layout"
              icon={<Calendar size={32} color="#22c55e" />}
              color="$green2"
              href="/(app)/planner"
            />
            <HubCard
              testID="shopping-card"
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
            testID="settings-button"
            chromeless
            icon={<Settings size={18} />}
            color="$gray10"
            justifyContent="flex-start"
            onPress={() => router.push('/(app)/settings')}
          >
            Settings
          </Button>
          <Button
            testID="signout-button"
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

/**
 * Planner Calendar Screen 📅
 * 
 * Week/4-day view of meal plan with slots.
 * Per frontend-redesign.md Section 2.4
 * 
 * Fun fact: Meal planning saves an average of $2,000/year on groceries! 💰
 */

import { useState, useMemo } from 'react';
import { ScrollView, Dimensions } from 'react-native';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter, Stack } from 'expo-router';
import {
  YStack,
  XStack,
  H2,
  H3,
  Text,
  Paragraph,
  Button,
  Card,
  Spinner,
} from 'tamagui';
import {
  Calendar,
  Plus,
  Lock,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  Sparkles,
} from '@tamagui/lucide-icons';

import { supabase } from '@/lib/supabase';
import { FAB } from '@/components/Core/Button';

const { width: SCREEN_WIDTH } = Dimensions.get('window');
const DAY_WIDTH = (SCREEN_WIDTH - 48) / 4;

type MealSlot = {
  id: string;
  date: string;
  meal_type: 'main' | 'side' | 'breakfast' | 'snack';
  recipe_id: string;
  recipe_title: string;
  locked: boolean;
};

type DayPlan = {
  date: string;
  dayName: string;
  isToday: boolean;
  slots: MealSlot[];
};

export default function PlannerScreen() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [weekOffset, setWeekOffset] = useState(0);

  // Calculate date range for current view
  const dateRange = useMemo(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const startDate = new Date(today);
    startDate.setDate(startDate.getDate() + weekOffset * 7);
    
    const dates: Date[] = [];
    for (let i = 0; i < 7; i++) {
      const d = new Date(startDate);
      d.setDate(d.getDate() + i);
      dates.push(d);
    }
    
    return dates;
  }, [weekOffset]);

  const startDateStr = dateRange[0].toISOString().split('T')[0];
  const endDateStr = dateRange[6].toISOString().split('T')[0];

  // Fetch meal plans for date range
  const { data: mealPlans, isLoading } = useQuery({
    queryKey: ['meal_plans', startDateStr, endDateStr],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('meal_plans')
        .select('*, recipes(title)')
        .gte('date', startDateStr)
        .lte('date', endDateStr)
        .order('date');

      if (error) throw error;
      return data?.map((mp) => ({
        ...mp,
        recipe_title: mp.recipes?.title || 'Unknown Recipe',
      })) as MealSlot[];
    },
  });

  // Toggle lock mutation
  const toggleLock = useMutation({
    mutationFn: async ({ id, locked }: { id: string; locked: boolean }) => {
      const { error } = await supabase
        .from('meal_plans')
        .update({ locked: !locked })
        .eq('id', id);
      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['meal_plans'] });
    },
  });

  // Reroll slot mutation (Phase 6)
  const rerollSlot = useMutation({
    mutationFn: async (slotId: string) => {
      // In real implementation, call LLM to suggest new recipe
      // For now, just invalidate to show loading
      await new Promise((r) => setTimeout(r, 1000));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['meal_plans'] });
    },
  });

  // Build day plans
  const dayPlans: DayPlan[] = useMemo(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const todayStr = today.toISOString().split('T')[0];

    return dateRange.map((date) => {
      const dateStr = date.toISOString().split('T')[0];
      const daySlots = mealPlans?.filter((mp) => mp.date === dateStr) || [];
      
      return {
        date: dateStr,
        dayName: date.toLocaleDateString('en-US', { weekday: 'short' }),
        isToday: dateStr === todayStr,
        slots: daySlots,
      };
    });
  }, [dateRange, mealPlans]);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.getDate().toString();
  };

  return (
    <>
      <Stack.Screen
        options={{
          headerRight: () => (
            <Button
              testID="new-plan-button"
              size="$3"
              theme="green"
              icon={<Sparkles size={18} />}
              onPress={() => router.push('/(app)/planner/new')}
              marginRight="$2"
            >
              New Plan
            </Button>
          ),
        }}
      />

      <YStack flex={1} backgroundColor="$background">
        {/* Week Navigation */}
        <XStack
          justifyContent="space-between"
          alignItems="center"
          padding="$4"
          borderBottomWidth={1}
          borderBottomColor="$gray4"
        >
          <Button
            testID="prev-week-button"
            size="$3"
            circular
            chromeless
            icon={<ChevronLeft size={20} />}
            onPress={() => setWeekOffset((o) => o - 1)}
          />
          <Text fontWeight="600" color="$gray11">
            {dateRange[0].toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
            })}{' '}
            -{' '}
            {dateRange[6].toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
            })}
          </Text>
          <Button
            testID="next-week-button"
            size="$3"
            circular
            chromeless
            icon={<ChevronRight size={20} />}
            onPress={() => setWeekOffset((o) => o + 1)}
          />
        </XStack>

        {isLoading ? (
          <YStack flex={1} justifyContent="center" alignItems="center">
            <Spinner size="large" color="$green10" />
          </YStack>
        ) : (
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            <XStack padding="$2">
              {dayPlans.map((day) => (
                <YStack
                  key={day.date}
                  width={DAY_WIDTH}
                  marginHorizontal="$1"
                  testID={`day-column-${day.date}`}
                >
                  {/* Day Header */}
                  <YStack
                    alignItems="center"
                    padding="$2"
                    backgroundColor={day.isToday ? '$green3' : '$gray2'}
                    borderRadius="$3"
                    marginBottom="$2"
                  >
                    <Text
                      fontSize="$2"
                      color={day.isToday ? '$green11' : '$gray10'}
                    >
                      {day.dayName}
                    </Text>
                    <Text
                      fontSize="$5"
                      fontWeight="bold"
                      color={day.isToday ? '$green11' : '$gray12'}
                    >
                      {formatDate(day.date)}
                    </Text>
                  </YStack>

                  {/* Meal Slots */}
                  <YStack space="$2">
                    {day.slots.length === 0 ? (
                      <Card
                        bordered
                        padding="$3"
                        opacity={0.5}
                        pressStyle={{ scale: 0.98 }}
                        onPress={() => router.push('/(app)/planner/new')}
                      >
                        <Text
                          fontSize="$2"
                          color="$gray10"
                          textAlign="center"
                        >
                          + Add
                        </Text>
                      </Card>
                    ) : (
                      day.slots.map((slot) => (
                        <Card
                          key={slot.id}
                          bordered
                          padding="$2"
                          testID={`slot-${slot.id}`}
                          pressStyle={{ scale: 0.98 }}
                          onPress={() =>
                            router.push(`/(app)/recipes/${slot.recipe_id}`)
                          }
                        >
                          <Text
                            fontSize="$2"
                            numberOfLines={2}
                            color="$gray12"
                          >
                            {slot.recipe_title}
                          </Text>
                          <XStack
                            justifyContent="flex-end"
                            marginTop="$1"
                            space="$1"
                          >
                            <Button
                              size="$1"
                              circular
                              chromeless
                              icon={
                                <Lock
                                  size={12}
                                  color={slot.locked ? '$green10' : '$gray8'}
                                />
                              }
                              onPress={() =>
                                toggleLock.mutate({
                                  id: slot.id,
                                  locked: slot.locked,
                                })
                              }
                              testID={`lock-${slot.id}`}
                            />
                            {!slot.locked && (
                              <Button
                                size="$1"
                                circular
                                chromeless
                                icon={<RefreshCw size={12} color="$orange10" />}
                                onPress={() => rerollSlot.mutate(slot.id)}
                                testID={`reroll-${slot.id}`}
                              />
                            )}
                          </XStack>
                        </Card>
                      ))
                    )}
                  </YStack>
                </YStack>
              ))}
            </XStack>
          </ScrollView>
        )}

        {/* Empty State */}
        {!isLoading && mealPlans?.length === 0 && (
          <YStack
            position="absolute"
            top="40%"
            left={0}
            right={0}
            alignItems="center"
            padding="$6"
          >
            <Calendar size={60} color="$gray8" />
            <H3 marginTop="$3" color="$gray11">
              No meals planned
            </H3>
            <Paragraph color="$gray10" textAlign="center">
              Tap "New Plan" to let AI suggest meals for the week!
            </Paragraph>
          </YStack>
        )}

        {/* FAB */}
        <FAB
          testID="generate-plan-fab"
          icon={<Sparkles size={24} color="white" />}
          backgroundColor="$green10"
          onPress={() => router.push('/(app)/planner/new')}
        />
      </YStack>
    </>
  );
}

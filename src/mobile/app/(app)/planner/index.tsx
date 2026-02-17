/**
 * Planner Calendar Screen 📅
 * 
 * Week view of meal plan with clear, labeled actions.
 * Simplified UX: one clear path to plan meals.
 * 
 * Fun fact: Meal planning saves an average of $2,000/year on groceries! 💰
 */

import { useState, useMemo } from 'react';
import { ScrollView } from 'react-native';
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
  Separator,
} from 'tamagui';
import {
  Calendar,
  Plus,
  Lock,
  Unlock,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Trash2,
  ShoppingCart,
  ArrowRight,
} from '@tamagui/lucide-icons';

import { supabase } from '@/lib/supabase';
import { useHouseholdId } from '@/hooks/useInventorySubscription';
import { guessCategory } from '@/lib/categories';
import { ConfirmDialog } from '@/components/Core/ConfirmDialog';

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
  dayNum: string;
  isToday: boolean;
  slots: MealSlot[];
};

export default function PlannerScreen() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const householdId = useHouseholdId();
  const [weekOffset, setWeekOffset] = useState(0);
  const [deleteSlot, setDeleteSlot] = useState<MealSlot | null>(null);

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

  // Remove meal mutation
  const removeMeal = useMutation({
    mutationFn: async (slotId: string) => {
      const { error } = await supabase
        .from('meal_plans')
        .delete()
        .eq('id', slotId);
      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['meal_plans'] });
    },
  });

  // Generate shopping list from all assigned meals
  const generateShoppingList = useMutation({
    mutationFn: async () => {
      if (!householdId || !mealPlans?.length) return;
      const recipeIds = [...new Set(mealPlans.map((mp) => mp.recipe_id))];
      const apiUrl = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:5300';

      const allIngredients: string[] = [];
      for (const rid of recipeIds) {
        const res = await fetch(`${apiUrl}/api/v1/recipes/${rid}`);
        if (!res.ok) continue;
        const recipe = await res.json();
        for (const ing of recipe.ingredients || []) {
          allIngredients.push(ing.item_name || ing.raw_text || 'unknown');
        }
      }

      const { data: existing } = await supabase
        .from('shopping_list')
        .select('name')
        .eq('household_id', householdId)
        .eq('checked', false);
      const existingNames = new Set((existing || []).map((e: { name: string }) => e.name.toLowerCase()));
      const unique = [...new Set(allIngredients.map((n) => n.toLowerCase()))]
        .filter((name) => !existingNames.has(name));
      const rows = unique.map((name) => ({
        household_id: householdId,
        name,
        category: guessCategory(name),
        checked: false,
      }));
      if (rows.length > 0) {
        const { error } = await supabase.from('shopping_list').insert(rows);
        if (error) throw error;
      }
      return unique.length;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shopping_list'] });
      router.push('/(app)/shopping');
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
        dayName: date.toLocaleDateString('en-US', { weekday: 'long' }),
        dayNum: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        isToday: dateStr === todayStr,
        slots: daySlots,
      };
    });
  }, [dateRange, mealPlans]);

  return (
    <>
      <Stack.Screen options={{ title: 'Meal Planner', headerShown: true }} />

      <YStack flex={1} backgroundColor="$background" maxWidth={700} width="100%" alignSelf="center">
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
            chromeless
            icon={<ChevronLeft size={20} />}
            onPress={() => setWeekOffset((o) => o - 1)}
            disabled={weekOffset <= 0}
            opacity={weekOffset <= 0 ? 0.3 : 1}
            cursor="pointer"
          >
            Prev
          </Button>
          <Text fontWeight="600" fontSize="$4" color="$gray12">
            {weekOffset === 0 ? 'This Week' : 
             weekOffset === 1 ? 'Next Week' :
             `${dateRange[0].toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} – ${dateRange[6].toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`}
          </Text>
          <Button
            testID="next-week-button"
            size="$3"
            chromeless
            icon={<ChevronRight size={20} />}
            onPress={() => setWeekOffset((o) => o + 1)}
            cursor="pointer"
          >
            Next
          </Button>
        </XStack>

        {isLoading ? (
          <YStack flex={1} justifyContent="center" alignItems="center">
            <Spinner size="large" color="$green10" />
          </YStack>
        ) : (
          <ScrollView contentContainerStyle={{ padding: 16, paddingBottom: 120 }}>
            {/* Day-by-day vertical list */}
            {dayPlans.map((day) => (
              <YStack key={day.date} marginBottom="$4" testID={`day-column-${day.date}`}>
                {/* Day Header */}
                <XStack
                  alignItems="center"
                  space="$2"
                  marginBottom="$2"
                >
                  <YStack
                    paddingHorizontal="$3"
                    paddingVertical="$1"
                    backgroundColor={day.isToday ? '$green4' : '$gray3'}
                    borderRadius="$3"
                  >
                    <Text
                      fontSize="$3"
                      fontWeight="bold"
                      color={day.isToday ? '$green11' : '$gray11'}
                    >
                      {day.dayName}
                    </Text>
                  </YStack>
                  <Text fontSize="$2" color="$gray10">{day.dayNum}</Text>
                  {day.isToday && (
                    <Text fontSize="$2" color="$green10" fontWeight="600">Today</Text>
                  )}
                </XStack>

                {/* Meal Cards */}
                {day.slots.length === 0 ? (
                  <Card
                    bordered
                    borderWidth={1}
                    borderStyle="dashed"
                    borderColor="$gray6"
                    backgroundColor="$gray2"
                    padding="$3"
                    pressStyle={{ scale: 0.98, backgroundColor: '$gray3' }}
                    hoverStyle={{ borderColor: '$gray8' }}
                    cursor="pointer"
                    onPress={() => 
                      router.push({
                        pathname: '/(app)/planner/add',
                        params: { date: day.date, meal_type: 'main' }
                      })
                    }
                  >
                    <XStack alignItems="center" justifyContent="center" space="$2">
                      <Plus size={16} color="$gray9" />
                      <Text fontSize="$3" color="$gray9">
                        Add a meal
                      </Text>
                    </XStack>
                  </Card>
                ) : (
                  <YStack space="$2">
                    {day.slots.map((slot) => (
                      <Card
                        key={slot.id}
                        bordered
                        padding="$3"
                        testID={`slot-${slot.id}`}
                        backgroundColor={slot.locked ? '$green2' : '$background'}
                        borderColor={slot.locked ? '$green6' : '$gray5'}
                      >
                        <XStack justifyContent="space-between" alignItems="center">
                          {/* Recipe name — tappable */}
                          <Text
                            fontSize="$4"
                            fontWeight="500"
                            color="$gray12"
                            flex={1}
                            cursor="pointer"
                            onPress={() =>
                              router.push(`/(app)/recipes/${slot.recipe_id}`)
                            }
                          >
                            {slot.recipe_title}
                          </Text>

                          {/* Action buttons — clearly labeled */}
                          <XStack space="$2" alignItems="center">
                            <Button
                              size="$2"
                              chromeless
                              cursor="pointer"
                              icon={slot.locked ? 
                                <Lock size={14} color="$green10" /> : 
                                <Unlock size={14} color="$gray8" />
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
                                size="$2"
                                chromeless
                                cursor="pointer"
                                icon={<Trash2 size={14} color="$red9" />}
                                onPress={() => setDeleteSlot(slot)}
                                testID={`remove-${slot.id}`}
                              />
                            )}
                          </XStack>
                        </XStack>
                      </Card>
                    ))}
                    {/* Add another meal to this day */}
                    <Button
                      size="$3"
                      chromeless
                      icon={<Plus size={14} color="$gray9" />}
                      cursor="pointer"
                      onPress={() =>
                        router.push({
                          pathname: '/(app)/planner/add',
                          params: { date: day.date, meal_type: 'side' }
                        })
                      }
                    >
                      <Text fontSize="$2" color="$gray9">Add another</Text>
                    </Button>
                  </YStack>
                )}
              </YStack>
            ))}
          </ScrollView>
        )}

        {/* Bottom Action Bar */}
        <YStack
          padding="$3"
          borderTopWidth={1}
          borderTopColor="$gray4"
          backgroundColor="$background"
          space="$2"
        >
          {/* Generate Shopping List — only when meals exist */}
          {!isLoading && mealPlans && mealPlans.length > 0 && (
            <Button
              testID="generate-shopping-button"
              size="$4"
              theme="blue"
              cursor="pointer"
              icon={
                generateShoppingList.isPending ? (
                  <Spinner size="small" />
                ) : (
                  <ShoppingCart size={18} />
                )
              }
              onPress={() => generateShoppingList.mutate()}
              disabled={generateShoppingList.isPending}
            >
              {generateShoppingList.isPending
                ? 'Generating...'
                : `Generate Shopping List (${mealPlans.length} meals)`}
            </Button>
          )}

          {/* AI Plan button — always visible */}
          <Button
            testID="generate-plan-button"
            size="$4"
            theme="green"
            cursor="pointer"
            icon={<Sparkles size={18} />}
            onPress={() => router.push('/(app)/planner/new')}
          >
            Generate AI Meal Plan
          </Button>
        </YStack>
      </YStack>

      {/* Delete Confirmation */}
      <ConfirmDialog
        open={!!deleteSlot}
        title="Remove Meal"
        message={`Remove "${deleteSlot?.recipe_title}" from the plan?`}
        confirmText="Remove"
        onConfirm={() => {
          if (deleteSlot) removeMeal.mutate(deleteSlot.id);
          setDeleteSlot(null);
        }}
        onCancel={() => setDeleteSlot(null)}
      />
    </>
  );
}

/**
 * New Plan Generator Screen 🎲
 * 
 * Configure and generate a new meal plan with AI.
 * Per frontend-redesign.md Section 2.4 (Phase 5)
 * 
 * Fun fact: Variety in meal planning increases nutrient intake by 30%! 🥗
 */

import { useState } from 'react';
import { ScrollView } from 'react-native';
import { useMutation } from '@tanstack/react-query';
import { useRouter, Stack } from 'expo-router';
import {
  YStack,
  XStack,
  H2,
  H3,
  Text,
  Paragraph,
  Button,
  Input,
  Card,
  Slider,
  Switch,
  Spinner,
} from 'tamagui';
import { Sparkles, Leaf, Fish, Flame, Clock, Wheat } from '@tamagui/lucide-icons';

import { KitchenButton } from '@/components/Core/Button';

type Constraint = {
  id: string;
  label: string;
  icon: React.ReactNode;
  enabled: boolean;
};

export default function NewPlanScreen() {
  const router = useRouter();
  
  // Form state
  const [daysToplan, setDaysToplan] = useState(3);
  const [constraints, setConstraints] = useState<Constraint[]>([
    { id: 'vegetarian', label: 'Vegetarian', icon: <Leaf size={18} color="$green10" />, enabled: false },
    { id: 'pescatarian', label: 'Pescatarian', icon: <Fish size={18} color="$blue10" />, enabled: false },
    { id: 'low-carb', label: 'Low Carb', icon: <Wheat size={18} color="$yellow10" />, enabled: false },
    { id: 'quick', label: 'Under 30 min', icon: <Clock size={18} color="$orange10" />, enabled: false },
    { id: 'spicy', label: 'Spicy', icon: <Flame size={18} color="$red10" />, enabled: false },
  ]);
  const [usePantry, setUsePantry] = useState(true);

  const toggleConstraint = (id: string) => {
    setConstraints((prev) =>
      prev.map((c) => (c.id === id ? { ...c, enabled: !c.enabled } : c))
    );
  };

  // Generate mutation
  const generatePlan = useMutation({
    mutationFn: async () => {
      // In production, call the planner LLM endpoint
      // For now, simulate the call
      await new Promise((r) => setTimeout(r, 2000));
      
      // Return mock data that would come from the API
      return {
        options: [
          {
            id: '1',
            theme: 'Comfort Classics',
            description: 'Hearty, familiar dishes that feel like home.',
            emoji: '🍝',
          },
          {
            id: '2',
            theme: 'Global Explorer',
            description: 'Travel the world through your taste buds.',
            emoji: '🌍',
          },
          {
            id: '3',
            theme: 'Healthy & Fresh',
            description: 'Light, nutritious meals for peak energy.',
            emoji: '🥗',
          },
        ],
      };
    },
    onSuccess: (data) => {
      // Navigate to preview with the generated options
      router.push({
        pathname: '/(app)/planner/preview',
        params: { options: JSON.stringify(data.options) },
      });
    },
  });

  return (
    <>
      <Stack.Screen
        options={{
          headerRight: () => (
            <Button
              testID="close-new-plan"
              size="$3"
              chromeless
              onPress={() => router.back()}
            >
              Cancel
            </Button>
          ),
        }}
      />

      <ScrollView contentContainerStyle={{ padding: 16, paddingBottom: 100 }}>
        <YStack space="$6">
          {/* Days Selector */}
          <YStack>
            <H3 testID="days-header">Days to Plan</H3>
            <Paragraph color="$gray10" marginBottom="$3">
              How many days ahead would you like to plan?
            </Paragraph>
            
            <Card bordered padding="$4">
              <XStack justifyContent="space-between" alignItems="center">
                <Input
                  testID="days-input"
                  placeholder="Days to plan (e.g. 3)"
                  value={daysToplan.toString()}
                  onChangeText={(v) => setDaysToplan(parseInt(v) || 1)}
                  keyboardType="numeric"
                  width={150}
                />
                <Text fontSize="$8" fontWeight="bold" color="$green11">
                  {daysToplan} {daysToplan === 1 ? 'day' : 'days'}
                </Text>
              </XStack>
              
              <Slider
                testID="days-slider"
                value={[daysToplan]}
                min={1}
                max={7}
                step={1}
                onValueChange={(vals) => setDaysToplan(vals[0])}
                marginTop="$3"
              >
                <Slider.Track backgroundColor="$gray5">
                  <Slider.TrackActive backgroundColor="$green10" />
                </Slider.Track>
                <Slider.Thumb index={0} circular size="$2" backgroundColor="$green10" />
              </Slider>
            </Card>
          </YStack>

          {/* Constraints */}
          <YStack>
            <H3 testID="constraints-header">Constraints</H3>
            <Paragraph color="$gray10" marginBottom="$3">
              Set dietary preferences for your meal plan.
            </Paragraph>
            
            <Card bordered padding="$3">
              <YStack space="$3">
                {constraints.map((constraint) => (
                  <XStack
                    key={constraint.id}
                    justifyContent="space-between"
                    alignItems="center"
                    testID={`constraint-${constraint.id}`}
                  >
                    <XStack space="$2" alignItems="center">
                      {constraint.icon}
                      <Text
                        testID={`constraint-label-${constraint.id}`}
                        aria-label={constraint.label}
                      >
                        {constraint.label}
                      </Text>
                    </XStack>
                    <Switch
                      testID={`constraint-toggle-${constraint.id}`}
                      aria-label={constraint.label}
                      size="$3"
                      checked={constraint.enabled}
                      onCheckedChange={() => toggleConstraint(constraint.id)}
                    >
                      <Switch.Thumb animation="bouncy" />
                    </Switch>
                  </XStack>
                ))}
              </YStack>
            </Card>
          </YStack>

          {/* Pantry Priority */}
          <YStack>
            <H3>Use What You Have</H3>
            <Paragraph color="$gray10" marginBottom="$3">
              Prioritize recipes using ingredients from your pantry.
            </Paragraph>
            
            <Card bordered padding="$4">
              <XStack justifyContent="space-between" alignItems="center">
                <YStack flex={1} marginRight="$3">
                  <Text fontWeight="600">Pantry-First Planning</Text>
                  <Text fontSize="$2" color="$gray10">
                    Reduces waste and shopping
                  </Text>
                </YStack>
                <Switch
                  testID="pantry-toggle"
                  size="$4"
                  checked={usePantry}
                  onCheckedChange={setUsePantry}
                >
                  <Switch.Thumb animation="bouncy" />
                </Switch>
              </XStack>
            </Card>
          </YStack>

          {/* Generate Button */}
          <KitchenButton
            testID="generate-button"
            size="$5"
            theme="green"
            icon={
              generatePlan.isPending ? (
                <Spinner size="small" color="white" />
              ) : (
                <Sparkles size={20} />
              )
            }
            onPress={() => generatePlan.mutate()}
            disabled={generatePlan.isPending}
          >
            {generatePlan.isPending ? 'Chewing on data...' : 'Generate Plan'}
          </KitchenButton>
        </YStack>
      </ScrollView>
    </>
  );
}

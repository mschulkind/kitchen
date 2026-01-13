/**
 * Cooking Mode Screen 👨‍🍳
 * 
 * Full-screen step-by-step cooking experience.
 * Per frontend-redesign.md Section 2.3
 * 
 * Fun fact: Following recipes step-by-step increases success rate by 70%! 📈
 */

import { useState, useEffect, useCallback } from 'react';
import { Dimensions, Pressable, StatusBar } from 'react-native';
import { useLocalSearchParams, useRouter, Stack } from 'expo-router';
import { useQuery } from '@tanstack/react-query';
import { useKeepAwake } from 'expo-keep-awake';
import {
  YStack,
  XStack,
  H1,
  H2,
  Text,
  Paragraph,
  Button,
  Spinner,
  Progress,
} from 'tamagui';
import {
  ChevronLeft,
  ChevronRight,
  X,
  CheckCircle2,
} from '@tamagui/lucide-icons';

import { supabase } from '@/lib/supabase';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

type Step = {
  order: number;
  instruction: string;
};

export default function CookingModeScreen() {
  // Keep screen awake during cooking
  useKeepAwake();

  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);
  const [isComplete, setIsComplete] = useState(false);

  // Fetch recipe steps
  const { data: recipe, isLoading } = useQuery({
    queryKey: ['recipe', id],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('recipes')
        .select('id, title, steps_json')
        .eq('id', id)
        .single();
      if (error) throw error;
      return data;
    },
    enabled: !!id,
  });

  const steps: Step[] = recipe?.steps_json || [];
  const totalSteps = steps.length;
  const progress = totalSteps > 0 ? ((currentStep + 1) / totalSteps) * 100 : 0;

  // Navigation handlers
  const goNext = useCallback(() => {
    if (currentStep < totalSteps - 1) {
      setCurrentStep((prev) => prev + 1);
    } else {
      setIsComplete(true);
    }
  }, [currentStep, totalSteps]);

  const goPrev = useCallback(() => {
    if (currentStep > 0) {
      setCurrentStep((prev) => prev - 1);
    }
  }, [currentStep]);

  const handleClose = useCallback(() => {
    router.back();
  }, [router]);

  // Handle completion
  const handleFinish = useCallback(async () => {
    // Record last cooked date
    await supabase
      .from('recipes')
      .update({ last_cooked_at: new Date().toISOString() })
      .eq('id', id);

    router.back();
  }, [id, router]);

  if (isLoading) {
    return (
      <YStack
        flex={1}
        justifyContent="center"
        alignItems="center"
        backgroundColor="$background"
      >
        <Spinner size="large" color="$orange10" />
      </YStack>
    );
  }

  if (isComplete) {
    return (
      <YStack
        flex={1}
        justifyContent="center"
        alignItems="center"
        padding="$6"
        backgroundColor="$green2"
        testID="cooking-complete-modal"
      >
        <StatusBar hidden />
        <CheckCircle2 size={80} color="#16a34a" />
        <H1 marginTop="$4" textAlign="center">
          Cooking Complete!
        </H1>
        <Paragraph
          color="$gray11"
          textAlign="center"
          marginTop="$2"
          maxWidth={280}
        >
          You've completed all {totalSteps} steps. Time to enjoy your creation!
        </Paragraph>
        <Button
          testID="finish-cooking-button"
          size="$5"
          theme="green"
          marginTop="$6"
          onPress={handleFinish}
        >
          Done Cooking
        </Button>
      </YStack>
    );
  }

  const currentStepData = steps[currentStep];

  return (
    <YStack flex={1} backgroundColor="$background">
      <StatusBar hidden />

      {/* Header */}
      <XStack
        paddingHorizontal="$4"
        paddingTop="$6"
        paddingBottom="$2"
        justifyContent="space-between"
        alignItems="center"
      >
        <Button
          testID="close-cooking-button"
          size="$3"
          circular
          chromeless
          icon={<X size={24} />}
          onPress={handleClose}
        />
        <Button
          testID="show-ingredients-button"
          size="$3"
          chromeless
          onPress={() => {/* TODO: show ingredients panel */}}
        >
          Ingredients
        </Button>
        <Text color="$gray10" fontSize="$3">
          {recipe?.title}
        </Text>
      </XStack>

      {/* Progress Bar */}
      <YStack paddingHorizontal="$4" marginBottom="$2">
        <Progress testID="progress-bar" value={progress} backgroundColor="$gray4" aria-valuenow={progress}>
          <Progress.Indicator backgroundColor="$orange10" animation="bouncy" />
        </Progress>
        <Text
          textAlign="center"
          color="$gray10"
          fontSize="$2"
          marginTop="$1"
        >
          Step {currentStep + 1} of {totalSteps}
        </Text>
      </YStack>

      {/* Step Content - Large Touch Zones */}
      <XStack flex={1}>
        {/* Left Zone - Previous */}
        <Pressable
          onPress={goPrev}
          style={{
            width: SCREEN_WIDTH * 0.25,
            justifyContent: 'center',
            alignItems: 'center',
          }}
          testID="prev-step-zone"
        >
          {currentStep > 0 && (
            <ChevronLeft size={40} color="$gray8" opacity={0.5} />
          )}
        </Pressable>

        {/* Center - Step Text */}
        <YStack
          flex={1}
          justifyContent="center"
          alignItems="center"
          paddingHorizontal="$4"
          testID={`cooking-step-${currentStep}`}
        >
          <Text testID="step-counter" color="$gray10" fontSize="$3" marginBottom="$2">
            Step {currentStep + 1}
          </Text>
          <H2
            testID="step-text"
            fontSize="$8"
            lineHeight="$9"
            textAlign="center"
            color="$gray12"
          >
            {currentStepData?.instruction || 'No instruction'}
          </H2>
        </YStack>

        {/* Right Zone - Next */}
        <Pressable
          onPress={goNext}
          style={{
            width: SCREEN_WIDTH * 0.25,
            justifyContent: 'center',
            alignItems: 'center',
          }}
          testID="next-step-zone"
        >
          <ChevronRight size={40} color="$orange10" />
        </Pressable>
      </XStack>

      {/* Bottom Navigation */}
      <XStack
        padding="$4"
        paddingBottom="$6"
        justifyContent="space-between"
        alignItems="center"
      >
        <Button
          testID="prev-step-button"
          size="$5"
          chromeless
          icon={<ChevronLeft size={24} />}
          disabled={currentStep === 0}
          opacity={currentStep === 0 ? 0.3 : 1}
          onPress={goPrev}
        >
          Back
        </Button>

        <Button
          testID="next-step-button"
          size="$5"
          theme="orange"
          iconAfter={<ChevronRight size={24} />}
          onPress={goNext}
        >
          {currentStep === totalSteps - 1 ? 'Finish' : 'Next'}
        </Button>
      </XStack>
    </YStack>
  );
}

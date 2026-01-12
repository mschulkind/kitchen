/**
 * Cooking Step Component 👨‍🍳
 * 
 * Large text display for cooking mode.
 * Designed for hands-free reading while cooking.
 * 
 * Fun fact: Voice commands are 3x faster than touch while cooking! 🗣️
 */

import { YStack, H2, Paragraph } from 'tamagui';

export interface CookingStepProps {
  /** Step number (1-indexed) */
  stepNumber: number;
  /** Total number of steps */
  totalSteps: number;
  /** Step instruction text */
  instruction: string;
  /** Timer duration in seconds (optional) */
  timerSeconds?: number;
}

/**
 * Full-screen cooking step display.
 * Large font for easy reading from a distance.
 */
export function CookingStep({
  stepNumber,
  totalSteps,
  instruction,
  timerSeconds,
}: CookingStepProps) {
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <YStack
      flex={1}
      justifyContent="center"
      alignItems="center"
      padding="$6"
      backgroundColor="$background"
      testID={`cooking-step-${stepNumber}`}
    >
      {/* Step Counter */}
      <Paragraph
        fontSize="$3"
        color="$gray10"
        marginBottom="$4"
      >
        Step {stepNumber} of {totalSteps}
      </Paragraph>

      {/* Instruction Text - Large for readability */}
      <H2
        fontSize="$9"
        textAlign="center"
        lineHeight="$9"
        color="$gray12"
        marginBottom="$6"
      >
        {instruction}
      </H2>

      {/* Optional Timer Display */}
      {timerSeconds !== undefined && (
        <Paragraph
          fontSize="$8"
          fontWeight="bold"
          color="$orange10"
        >
          ⏱️ {formatTime(timerSeconds)}
        </Paragraph>
      )}
    </YStack>
  );
}

export default CookingStep;

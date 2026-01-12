/**
 * Planner Screen 📅
 * 
 * Placeholder for Phase 5: Planner Core.
 */

import { YStack, Text, H1, Paragraph, Button } from 'tamagui';
import { Calendar, Sparkles } from '@tamagui/lucide-icons';

export default function PlannerScreen() {
  return (
    <YStack flex={1} justifyContent="center" alignItems="center" padding="$6" backgroundColor="$background">
      <Calendar size={80} color="#16a34a" />
      <H1 marginTop="$4">Meal Planner</H1>
      <Paragraph color="$gray10" textAlign="center" marginTop="$2">
        The "Choose Your Own Adventure" planner is coming in Phase 5! 🎲
      </Paragraph>
      <Button 
        size="$5" 
        theme="green" 
        marginTop="$6"
        icon={<Sparkles size={20} />}
        disabled
      >
        Start Planning (Coming Soon)
      </Button>
    </YStack>
  );
}

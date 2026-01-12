/**
 * Shopping List Screen 🛒
 * 
 * Placeholder for Phase 7: Shopping List.
 */

import { YStack, Text, H1, Paragraph, Button } from 'tamagui';
import { ShoppingCart, CheckSquare } from '@tamagui/lucide-icons';

export default function ShoppingScreen() {
  return (
    <YStack flex={1} justifyContent="center" alignItems="center" padding="$6" backgroundColor="$background">
      <ShoppingCart size={80} color="#f59e0b" />
      <H1 marginTop="$4">Shopping List</H1>
      <Paragraph color="$gray10" textAlign="center" marginTop="$2">
        Realtime synced shopping lists are coming in Phase 7! ✨
      </Paragraph>
      <Paragraph color="$gray9" textAlign="center" fontSize="$3" marginTop="$2">
        Shop together with family - checkmarks sync instantly!
      </Paragraph>
      <Button 
        size="$5" 
        theme="orange" 
        marginTop="$6"
        icon={<CheckSquare size={20} />}
        disabled
      >
        View List (Coming Soon)
      </Button>
    </YStack>
  );
}

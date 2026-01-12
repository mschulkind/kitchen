/**
 * Screen Layout Component 📱
 * 
 * Wrapper component with SafeAreaView and standard padding.
 * Ensures consistent screen layout across the app.
 * 
 * Fun fact: SafeAreaView was introduced for iPhone X's notch! 📲
 */

import { ReactNode } from 'react';
import { YStack, YStackProps, ScrollView } from 'tamagui';
import { SafeAreaView } from 'react-native-safe-area-context';

export interface ScreenProps extends YStackProps {
  /** Test ID for E2E selection */
  testID?: string;
  /** Content to render */
  children: ReactNode;
  /** Enable scrolling (default: false) */
  scrollable?: boolean;
  /** Add standard padding (default: true) */
  padded?: boolean;
}

/**
 * Screen wrapper with safe area insets.
 * Use this as the root component for all screens.
 */
export function Screen({
  children,
  testID,
  scrollable = false,
  padded = true,
  ...props
}: ScreenProps) {
  const content = (
    <YStack
      flex={1}
      backgroundColor="$background"
      padding={padded ? '$4' : 0}
      {...props}
    >
      {children}
    </YStack>
  );

  return (
    <SafeAreaView style={{ flex: 1 }} testID={testID}>
      {scrollable ? (
        <ScrollView 
          contentContainerStyle={{ flexGrow: 1 }}
          showsVerticalScrollIndicator={false}
        >
          {content}
        </ScrollView>
      ) : (
        content
      )}
    </SafeAreaView>
  );
}

export default Screen;

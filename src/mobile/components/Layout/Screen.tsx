/**
 * Screen Layout Component 📱
 * 
 * Wrapper component with SafeAreaView and standard padding.
 * Ensures consistent screen layout across the app.
 * Centers content with max-width on desktop for readability.
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
  /** Max width for desktop centering (default: 800) */
  maxContentWidth?: number;
}

/**
 * Screen wrapper with safe area insets.
 * Use this as the root component for all screens.
 * Content is centered with max-width on wide screens.
 */
export function Screen({
  children,
  testID,
  scrollable = false,
  padded = true,
  maxContentWidth = 800,
  ...props
}: ScreenProps) {
  const content = (
    <YStack
      flex={1}
      backgroundColor="$background"
      padding={padded ? '$4' : 0}
      width="100%"
      maxWidth={maxContentWidth}
      alignSelf="center"
      {...props}
    >
      {children}
    </YStack>
  );

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: 'var(--background, #fff)' }} testID={testID}>
      {scrollable ? (
        <ScrollView 
          contentContainerStyle={{ flexGrow: 1, alignItems: 'center' }}
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

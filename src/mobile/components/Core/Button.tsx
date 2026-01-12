/**
 * Kitchen Button Component 🔘
 * 
 * Wrapper around Tamagui Button enforcing 44px minimum touch target.
 * Per AGENTS.md: "large touch targets (min 44x44px)"
 * 
 * Fun fact: Apple's HIG recommends 44pt for comfortable finger taps! 👆
 */

import { Button, ButtonProps, styled } from 'tamagui';
import { forwardRef } from 'react';

export interface KitchenButtonProps extends ButtonProps {
  /** Test ID for E2E selection */
  testID?: string;
}

/**
 * Primary button component with enforced touch target size.
 * Use this instead of raw Tamagui Button throughout the app.
 */
export const KitchenButton = forwardRef<typeof Button, KitchenButtonProps>(
  ({ children, testID, ...props }, ref) => {
    return (
      <Button
        ref={ref}
        testID={testID}
        minHeight={44}
        minWidth={44}
        paddingHorizontal="$4"
        pressStyle={{ scale: 0.97, opacity: 0.9 }}
        animation="quick"
        {...props}
      >
        {children}
      </Button>
    );
  }
);

KitchenButton.displayName = 'KitchenButton';

/**
 * Primary action button (filled)
 */
export const PrimaryButton = styled(KitchenButton, {
  name: 'PrimaryButton',
  backgroundColor: '$kitchenPrimary',
  color: 'white',
  fontWeight: '600',
});

/**
 * Secondary action button (outlined)
 */
export const SecondaryButton = styled(KitchenButton, {
  name: 'SecondaryButton',
  backgroundColor: 'transparent',
  borderWidth: 1,
  borderColor: '$kitchenPrimary',
  color: '$kitchenPrimary',
});

/**
 * Floating Action Button (FAB)
 */
export const FAB = styled(KitchenButton, {
  name: 'FAB',
  width: 56,
  height: 56,
  borderRadius: 28,
  position: 'absolute',
  bottom: 24,
  right: 24,
  elevation: 4,
  shadowColor: '$shadowColor',
  shadowOffset: { width: 0, height: 2 },
  shadowOpacity: 0.25,
  shadowRadius: 4,
  backgroundColor: '$kitchenPrimary',
});

export default KitchenButton;

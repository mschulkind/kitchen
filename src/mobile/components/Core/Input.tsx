/**
 * Kitchen Input Component 📝
 * 
 * Standardized text input with 44px minimum touch target.
 * Per AGENTS.md Mobile-First Principles.
 * 
 * Fun fact: The average mobile user types 38 words per minute! ⌨️
 */

import { Input, InputProps, styled, XStack, Text } from 'tamagui';
import { forwardRef } from 'react';

export interface KitchenInputProps extends InputProps {
  /** Test ID for E2E selection */
  testID?: string;
  /** Optional label above input */
  label?: string;
  /** Error message to display */
  error?: string;
}

/**
 * Primary input component with enforced touch target size.
 * Use this instead of raw Tamagui Input throughout the app.
 */
export const KitchenInput = forwardRef<typeof Input, KitchenInputProps>(
  ({ testID, label, error, ...props }, ref) => {
    return (
      <>
        {label && (
          <Text fontSize="$3" color="$gray11" marginBottom="$1">
            {label}
          </Text>
        )}
        <Input
          ref={ref}
          testID={testID}
          minHeight={44}
          paddingHorizontal="$3"
          borderRadius="$4"
          borderWidth={1}
          borderColor={error ? '$red8' : '$gray6'}
          backgroundColor="$gray2"
          placeholderTextColor="$gray9"
          fontSize="$4"
          {...props}
        />
        {error && (
          <Text fontSize="$2" color="$red10" marginTop="$1">
            {error}
          </Text>
        )}
      </>
    );
  }
);

KitchenInput.displayName = 'KitchenInput';

/**
 * Search input with icon styling
 */
export const SearchInput = styled(KitchenInput, {
  name: 'SearchInput',
  borderRadius: '$8',
  backgroundColor: '$gray3',
  borderWidth: 0,
});

export default KitchenInput;

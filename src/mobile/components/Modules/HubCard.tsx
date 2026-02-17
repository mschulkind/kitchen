/**
 * Hub Card Component 🏠
 * 
 * Large touch-friendly card for dashboard navigation.
 * Minimum 140px height for comfortable touch interaction.
 * 
 * Fun fact: Fitts's Law says larger targets are easier to hit! 🎯
 */

import { ReactNode } from 'react';
import { useRouter } from 'expo-router';
import { Card, YStack, H3, Paragraph, CardProps } from 'tamagui';

export interface HubCardProps extends Omit<CardProps, 'children'> {
  /** Card title */
  title: string;
  /** Card subtitle */
  subtitle: string;
  /** Icon element */
  icon: ReactNode;
  /** Background color token */
  color: string;
  /** Navigation route */
  href: string;
  /** Test ID for E2E selection */
  testID?: string;
}

/**
 * Dashboard navigation card with large touch target.
 * Use on the Hub screen for module entry points.
 */
export function HubCard({
  title,
  subtitle,
  icon,
  color,
  href,
  testID,
  ...props
}: HubCardProps) {
  const router = useRouter();

  return (
    <Card
      testID={testID}
      flex={1}
      height={140}
      backgroundColor={color}
      borderRadius="$6"
      pressStyle={{ scale: 0.96, opacity: 0.9 }}
      hoverStyle={{ scale: 1.02, opacity: 0.95 }}
      animation="bouncy"
      cursor="pointer"
      onPress={() => router.push(href as any)}
      justifyContent="center"
      alignItems="center"
      elevate
      role="button"
      aria-label={`${title}: ${subtitle}`}
      {...props}
    >
      <YStack alignItems="center" space="$2">
        {icon}
        <H3 fontSize="$5" color="$gray12">
          {title}
        </H3>
        <Paragraph fontSize="$2" color="$gray11">
          {subtitle}
        </Paragraph>
      </YStack>
    </Card>
  );
}

export default HubCard;

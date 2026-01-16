/**
 * Recipe Card Component 📖
 * 
 * Card component for displaying recipe summaries in lists.
 * Includes image, title, cook time, and last cooked date.
 * Shows a placeholder when no image is available.
 * 
 * Fun fact: The average recipe has 9 ingredients! 🧅
 */

import { useRouter } from 'expo-router';
import { Card, XStack, YStack, H4, Paragraph, Image } from 'tamagui';
import { Clock, Calendar, Image as ImageLucide } from '@tamagui/lucide-icons';

export interface RecipeCardProps {
  /** Recipe ID for navigation */
  id: string;
  /** Recipe title */
  title: string;
  /** Cook time in minutes */
  cookTime?: number;
  /** Last cooked human-readable date */
  lastCooked?: string;
  /** Recipe image URL */
  imageUrl?: string;
  /** Test ID override */
  testID?: string;
}

/**
 * Recipe list item card with image and metadata.
 * Automatically generates testID from id: recipe-card-{id}
 */
export function RecipeCard({
  id,
  title,
  cookTime,
  lastCooked,
  imageUrl,
  testID,
}: RecipeCardProps) {
  const router = useRouter();
  const cardTestId = testID || `recipe-card-${id.toLowerCase().replace(/\s+/g, '-')}`;

  return (
    <Card
      testID={cardTestId}
      bordered
      elevate
      size="$4"
      animation="bouncy"
      pressStyle={{ scale: 0.98 }}
      onPress={() => router.push(`/(app)/recipes/${id}`)}
      marginBottom="$3"
    >
      <XStack>
        {imageUrl ? (
          <Image
            testID="recipe-card-image"
            source={{ uri: imageUrl }}
            width={100}
            height={100}
            borderTopLeftRadius="$4"
            borderBottomLeftRadius="$4"
          />
        ) : (
          <YStack
            testID="recipe-image-placeholder"
            width={100}
            height={100}
            backgroundColor="$gray4"
            borderTopLeftRadius="$4"
            borderBottomLeftRadius="$4"
            justifyContent="center"
            alignItems="center"
          >
            <ImageLucide size={32} color="$gray8" />
          </YStack>
        )}
        <YStack flex={1} padding="$3" justifyContent="center">
          <H4 numberOfLines={2} color="$gray12">
            {title}
          </H4>
          <XStack space="$3" marginTop="$2">
            {cookTime && (
              <XStack space="$1" alignItems="center">
                <Clock size={14} color="$gray10" />
                <Paragraph fontSize="$2" color="$gray10">
                  {cookTime} min
                </Paragraph>
              </XStack>
            )}
            {lastCooked && (
              <XStack space="$1" alignItems="center">
                <Calendar size={14} color="$gray10" />
                <Paragraph fontSize="$2" color="$gray10">
                  {lastCooked}
                </Paragraph>
              </XStack>
            )}
          </XStack>
        </YStack>
      </XStack>
    </Card>
  );
}

export default RecipeCard;

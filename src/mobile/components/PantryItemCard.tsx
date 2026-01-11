/**
 * PantryItemCard Component 🥫
 * 
 * Displays a single pantry item with swipe-to-delete.
 * Touch-friendly design with large targets (44x44px min).
 */

import { Alert } from 'react-native';
import { Link } from 'expo-router';
import { XStack, YStack, Text, Card, Button } from 'tamagui';
import { Trash2, Edit3, AlertTriangle } from '@tamagui/lucide-icons';
import { Database } from '@/lib/supabase';

type PantryItem = Database['public']['Tables']['pantry_items']['Row'];

interface PantryItemCardProps {
  item: PantryItem;
  onDelete: () => void;
}

export function PantryItemCard({ item, onDelete }: PantryItemCardProps) {
  // Check if expiring soon (within 3 days)
  const isExpiringSoon = item.expiry_date && 
    new Date(item.expiry_date) <= new Date(Date.now() + 3 * 24 * 60 * 60 * 1000);
  
  // Check if expired
  const isExpired = item.expiry_date && 
    new Date(item.expiry_date) < new Date();

  const handleDelete = () => {
    Alert.alert(
      'Delete Item',
      `Are you sure you want to delete "${item.name}"?`,
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Delete', style: 'destructive', onPress: onDelete },
      ]
    );
  };

  return (
    <Card
      elevate
      size="$4"
      marginBottom="$2"
      animation="quick"
      pressStyle={{ scale: 0.98 }}
      borderLeftWidth={4}
      borderLeftColor={
        isExpired ? '$red10' :
        isExpiringSoon ? '$orange10' :
        '$green10'
      }
    >
      <Card.Header padded>
        <XStack justifyContent="space-between" alignItems="center">
          <YStack flex={1}>
            <XStack alignItems="center" space="$2">
              <Text fontSize="$5" fontWeight="600">
                {item.name}
              </Text>
              {(isExpired || isExpiringSoon) && (
                <AlertTriangle 
                  size={16} 
                  color={isExpired ? '#dc2626' : '#f59e0b'} 
                />
              )}
            </XStack>
            <Text fontSize="$3" color="$gray10">
              {item.quantity} {item.unit}
              {item.expiry_date && (
                <Text color={isExpired ? '$red10' : isExpiringSoon ? '$orange10' : '$gray10'}>
                  {' • '}Expires {new Date(item.expiry_date).toLocaleDateString()}
                </Text>
              )}
            </Text>
            {item.notes && (
              <Text fontSize="$2" color="$gray9" marginTop="$1">
                {item.notes}
              </Text>
            )}
          </YStack>

          <XStack space="$2">
            <Link href={`/inventory/${item.id}`} asChild>
              <Button
                size="$3"
                circular
                icon={<Edit3 size={16} />}
                chromeless
              />
            </Link>
            <Button
              size="$3"
              circular
              icon={<Trash2 size={16} color="#dc2626" />}
              chromeless
              onPress={handleDelete}
            />
          </XStack>
        </XStack>
      </Card.Header>
    </Card>
  );
}

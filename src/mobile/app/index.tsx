import { Redirect } from 'expo-router';
import { YStack, Spinner } from 'tamagui';

export default function Index() {
  return <Redirect href="/(auth)/landing" />;
}

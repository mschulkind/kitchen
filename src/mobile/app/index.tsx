// Redirect root to auth landing page by default
import { Redirect } from 'expo-router';

export default function Index() {
  return <Redirect href="/(auth)/landing" />;
}

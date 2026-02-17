/**
 * Recipes List Screen 📖
 * 
 * Main recipe collection view with search and FAB.
 * Per frontend-redesign.md Section 2.3
 * 
 * Fun fact: The average home cook knows about 10 recipes by heart! 🧠
 */

import { useState, useCallback } from 'react';
import { FlatList, RefreshControl } from 'react-native';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useRouter, Stack } from 'expo-router';
import {
  YStack,
  XStack,
  Text,
  Button,
  Input,
  Spinner,
  Sheet,
  H1,
  Paragraph,
} from 'tamagui';
import { Plus, Search, Link as LinkIcon, MessageCircle } from '@tamagui/lucide-icons';

import { supabase } from '@/lib/supabase';
import { RecipeCard } from '@/components/Modules/RecipeCard';
import { KitchenInput } from '@/components/Core/Input';
import { FAB } from '@/components/Core/Button';

type Recipe = {
  id: string;
  title: string;
  cook_time_minutes?: number;
  image_url?: string;
  last_cooked_at?: string;
  created_at: string;
};

export default function RecipesListScreen() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState('');
  const [showActionSheet, setShowActionSheet] = useState(false);
  const [showUrlDialog, setShowUrlDialog] = useState(false);
  const [importUrl, setImportUrl] = useState('');
  const [isImporting, setIsImporting] = useState(false);

  // Fetch recipes
  const { data: recipes, isLoading, refetch, isRefetching } = useQuery({
    queryKey: ['recipes'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('recipes')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) throw error;
      return data as Recipe[];
    },
  });

  // Filter by search
  const filteredRecipes = recipes?.filter((recipe) =>
    recipe.title.toLowerCase().includes(searchQuery.toLowerCase())
  ) ?? [];

  // Handle URL import
  const handleImportUrl = useCallback(async () => {
    if (!importUrl.trim()) return;
    
    setIsImporting(true);
    try {
      // Call recipe scraper API
      const apiUrl = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:5300';
      const response = await fetch(`${apiUrl}/api/v1/recipes/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: importUrl }),
      });
      
      if (!response.ok) throw new Error('Failed to import recipe');
      
      await queryClient.invalidateQueries({ queryKey: ['recipes'] });
      setShowUrlDialog(false);
      setImportUrl('');
    } catch (error) {
      console.error('Import failed:', error);
    } finally {
      setIsImporting(false);
    }
  }, [importUrl, queryClient]);

  // Render helper for relative time
  const formatLastCooked = (dateStr?: string) => {
    if (!dateStr) return undefined;
    const date = new Date(dateStr);
    const days = Math.floor((Date.now() - date.getTime()) / (1000 * 60 * 60 * 24));
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    return `${Math.floor(days / 7)} weeks ago`;
  };

  return (
    <>
      <Stack.Screen
        options={{
          headerRight: () => (
            <Button
              testID="import-recipe-fab"
              size="$3"
              circular
              icon={<Plus size={20} />}
              onPress={() => setShowUrlDialog(true)}
              marginRight="$2"
            />
          ),
        }}
      />

      <YStack flex={1} backgroundColor="$background" padding="$4" maxWidth={800} width="100%" alignSelf="center">
        {/* Search Bar */}
        <XStack marginBottom="$4">
          <KitchenInput
            flex={1}
            placeholder="Search recipes..."
            value={searchQuery}
            onChangeText={setSearchQuery}
            testID="recipe-search-input"
          />
        </XStack>

        {/* Recipe List */}
        {isLoading ? (
          <YStack flex={1} justifyContent="center" alignItems="center">
            <Spinner size="large" color="$orange10" />
          </YStack>
        ) : filteredRecipes.length === 0 ? (
          <YStack flex={1} justifyContent="center" alignItems="center" padding="$6">
            <Text fontSize="$6" marginBottom="$2">📖</Text>
            <H1 size="$6" color="$gray11">No recipes found</H1>
            <Paragraph color="$gray10" textAlign="center" marginTop="$2">
              {searchQuery 
                ? 'Try a different search term'
                : 'Import a recipe from a URL or chat with AI to craft one'}
            </Paragraph>
            <Button
              testID="add-first-recipe"
              marginTop="$4"
              theme="orange"
              icon={<Plus size={18} />}
              onPress={() => setShowUrlDialog(true)}
            >
              Add Recipe
            </Button>
          </YStack>
        ) : (
          <FlatList
            data={filteredRecipes}
            keyExtractor={(item) => item.id}
            renderItem={({ item }) => (
              <RecipeCard
                id={item.id}
                title={item.title}
                cookTime={item.cook_time_minutes}
                lastCooked={formatLastCooked(item.last_cooked_at)}
                imageUrl={item.image_url}
              />
            )}
            refreshControl={
              <RefreshControl refreshing={isRefetching} onRefresh={refetch} />
            }
            contentContainerStyle={{ paddingBottom: 80 }}
            testID="recipe-list"
          />
        )}

        {/* FAB */}
        <FAB
          testID="add-recipe-fab"
          icon={<Plus size={24} color="white" />}
          backgroundColor="$orange10"
          onPress={() => setShowActionSheet(true)}
        />

        {/* Action Sheet for Add Options — conditionally rendered to avoid ghost content on web */}
        {showActionSheet && (
          <Sheet
            modal
            open={showActionSheet}
            onOpenChange={setShowActionSheet}
            snapPoints={[35]}
            dismissOnSnapToBottom
          >
            <Sheet.Overlay />
            <Sheet.Frame padding="$4">
              <Sheet.Handle />
              <YStack space="$3" marginTop="$4">
                <H1 size="$5">Add Recipe</H1>
                
                <Button
                  testID="paste-url-option"
                  size="$5"
                  icon={<LinkIcon size={20} />}
                  onPress={() => {
                    setShowActionSheet(false);
                    setShowUrlDialog(true);
                  }}
                >
                  Import from URL
                </Button>
                
                <Button
                  testID="chat-recipe-option"
                  size="$5"
                  icon={<MessageCircle size={20} />}
                  chromeless
                  disabled
                >
                  Chat with AI (Coming Soon)
                </Button>
              </YStack>
            </Sheet.Frame>
          </Sheet>
        )}

        {/* URL Import Dialog — conditionally rendered to avoid ghost content on web */}
        {showUrlDialog && (
          <Sheet
            modal
            open={showUrlDialog}
            onOpenChange={setShowUrlDialog}
            snapPoints={[35]}
            dismissOnSnapToBottom
          >
            <Sheet.Overlay />
            <Sheet.Frame padding="$4">
              <Sheet.Handle />
              <YStack space="$4" marginTop="$4">
                <H1 size="$5">Import from URL</H1>
                
                <Input
                  placeholder="https://example.com/recipe"
                  value={importUrl}
                  onChangeText={setImportUrl}
                  autoCapitalize="none"
                  keyboardType="url"
                  testID="recipe-url-input"
                />
                
                {isImporting && (
                  <XStack space="$2" alignItems="center">
                    <Spinner size="small" />
                    <Text color="$gray10">Parsing recipe...</Text>
                  </XStack>
                )}
                
                <Button
                  theme="orange"
                  onPress={handleImportUrl}
                  disabled={!importUrl.trim() || isImporting}
                >
                  Import
                </Button>
              </YStack>
            </Sheet.Frame>
          </Sheet>
        )}
      </YStack>
    </>
  );
}

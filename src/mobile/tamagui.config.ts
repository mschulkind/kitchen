/**
 * Tamagui Configuration 🎨
 * 
 * Design system tokens and theme configuration.
 * Uses Tamagui's default config as a base with Kitchen customizations.
 * 
 * Fun fact: Tamagui compiles styles at build time for near-native performance! ⚡
 */

import { config as defaultConfig } from '@tamagui/config/v3';
import { createTamagui } from 'tamagui';

// Extend the default config with Kitchen-specific tokens
export const config = createTamagui({
  ...defaultConfig,
  
  // Custom theme tokens for Kitchen
  tokens: {
    ...defaultConfig.tokens,
    color: {
      ...defaultConfig.tokens.color,
      // Kitchen brand colors
      kitchenPrimary: '#2563eb',      // Blue - main actions
      kitchenSecondary: '#16a34a',    // Green - success/fresh
      kitchenWarning: '#f59e0b',      // Amber - expiring items
      kitchenDanger: '#dc2626',       // Red - expired/errors
      kitchenMuted: '#6b7280',        // Gray - secondary text
    },
  },
  
  // Responsive breakpoints (mobile-first per D3)
  media: {
    ...defaultConfig.media,
    xs: { maxWidth: 480 },
    sm: { maxWidth: 640 },
    md: { maxWidth: 768 },
    lg: { maxWidth: 1024 },
    xl: { maxWidth: 1280 },
  },
});

// Type exports for TypeScript
export type AppConfig = typeof config;

declare module 'tamagui' {
  interface TamaguiCustomConfig extends AppConfig {}
}

export default config;

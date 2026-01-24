/**
 * Inventory Route Redirect 📦➡️
 * 
 * This file handles the /inventory route and redirects to the proper
 * authenticated inventory page at /(app)/inventory.
 * 
 * Without this file, /inventory shows a blank page!
 * 
 * Fun fact: Expo Router uses file-based routing, so every accessible
 * URL needs a corresponding file! 🗂️
 */

import { Redirect } from 'expo-router';

export default function InventoryRedirect() {
  // Redirect to the authenticated inventory page
  return <Redirect href="/(app)/inventory" />;
}

// Learn more https://docs.expo.io/guides/customizing-metro
const { getDefaultConfig } = require('expo/metro-config');
const exclusionList = require('metro-config/private/defaults/exclusionList');

/** @type {import('expo/metro-config').MetroConfig} */
const config = getDefaultConfig(__dirname, {
  // Enable CSS support for Tamagui
  isCSSEnabled: true,
});

// Add Tamagui support
config.resolver.sourceExts.push('mjs');

// 🛡️ SECURITY: Exclude devlogin.tsx from production bundles completely
// This ensures the route code is not just hidden, but physically absent from the bundle.
if (process.env.NODE_ENV !== 'development') {
  config.resolver.blockList = exclusionList([
    /.*\/app\/devlogin\.tsx$/,
  ]);
}

module.exports = config;

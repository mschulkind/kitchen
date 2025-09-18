# Phase 1.5 Decision: Notifications Setup

## Table of Contents
- [Proposal](#proposal)
- [API Sketch](#api-sketch)
- [Client Handling](#client-handling)
- [Decision](#decision)

## Proposal

**This feature is currently on hold and will be revisited after the MVP.**

We will implement push notifications using a combination of Supabase Edge Functions and the Expo Notifications library. This approach aligns with our existing tech stack and provides a robust, scalable solution for alerting users to real-time events.

The flow will be as follows:
1. A database change (e.g., a new item added to a shared shopping list) triggers a Supabase database webhook.
2. The webhook invokes a Supabase Edge Function.
3. The Edge Function retrieves the necessary data (e.g., the user to be notified, the content of the message).
4. The Edge Function then sends a push notification to the relevant user(s) via the Expo Push API.
5. The Expo Notifications library on the client-side receives and handles the notification.

## API Sketch

The core of this system will be a Supabase Edge Function. This function will be responsible for sending the notification.

```typescript
// supabase/functions/send-notification/index.ts
import { serve } from "https://deno.land/std@0.131.0/http/server.ts";
import { Expo } from 'expo-server-sdk';

const expo = new Expo();

serve(async (req) => {
  const { userId, message, data } = await req.json();

  // Retrieve the user's push token from the database
  // (This assumes you have a table storing user push tokens)
  const { data: userData, error } = await supabase
    .from('user_push_tokens')
    .select('push_token')
    .eq('user_id', userId)
    .single();

  if (error || !userData) {
    return new Response(
      JSON.stringify({ error: 'User not found or no push token' }),
      { headers: { "Content-Type": "application/json" }, status: 404 }
    );
  }

  const pushToken = userData.push_token;

  if (!Expo.isExpoPushToken(pushToken)) {
    console.error(`Push token ${pushToken} is not a valid Expo push token`);
    return new Response(
      JSON.stringify({ error: 'Invalid push token' }),
      { headers: { "Content-Type": "application/json" }, status: 400 }
    );
  }

  const messages = [{
    to: pushToken,
    sound: 'default',
    body: message,
    data: data,
  }];

  const chunks = expo.chunkPushNotifications(messages);
  // ... (sending logic) ...

  return new Response(
    JSON.stringify({ success: true }),
    { headers: { "Content-Type": "application/json" } }
  )
});
```

This function will be triggered by a database webhook on the `shopping_list_items` table (and others as needed).

## Client Handling

On the React Native/Expo client, we will use the `expo-notifications` library to:
1.  **Request Permissions:** Ask the user for permission to send push notifications.
2.  **Retrieve Push Token:** Get the unique Expo Push Token for the device.
3.  **Store Token:** Send the push token to our backend to be stored in the `user_push_tokens` table, associated with the user.
4.  **Handle Notifications:** Set up listeners to handle incoming notifications when the app is in the foreground, background, or closed.

## Decision

**Date:** 2025-09-18

**Outcome:** The decision has been made to **defer** the implementation of push notifications until after the initial MVP launch. The proposed architecture using Supabase Edge Functions and Expo Notifications remains the likely approach for future implementation, but it is not a priority for the initial release.
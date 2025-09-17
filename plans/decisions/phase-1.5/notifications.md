# Decision Log: Notifications Setup

This document describes the plan for implementing push notifications to alert users of relevant activity.

*   **Phase:** 1.5
*   **Status:** Scoping
*   **Owner:** A.I. Assistant

## 1. Goal

To proactively inform users about important events within the app, such as when a collaborator updates a shared shopping list or a meal plan is updated. This enhances engagement and the collaborative experience.

## 2. Technical Strategy

We will use a combination of **Supabase Edge Functions** and the **Expo Notifications** library to deliver push notifications.

### Architecture:

1.  **Database Triggers:** A Postgres trigger will be placed on key tables (e.g., `shopping_list_items`, `meal_plans`).
2.  **Edge Function Invocation:** When a relevant change occurs (e.g., a new item is added to a shared list), the trigger will invoke a Supabase Edge Function.
3.  **Function Logic:** The Edge Function will contain the logic to determine who should be notified and what the message should be.
4.  **Push Notification Service:** The function will then send a request to a push notification service. For Expo, this involves sending a request to Expo's push notification service endpoint.
5.  **Client-Side Handling:** The Expo app will receive the push notification via the Expo Notifications library, which handles the platform-specific delivery (APNS for iOS, FCM for Android).

### API Sketch (Edge Function):

The function will be triggered by the database. Inside the function, we'll use the user's push token to send them a notification.

```typescript
// supabase/functions/send-notification/index.ts
import { serve } from "https://deno.land/std@0.131.0/http/server.ts";
import { Expo } from 'expo-server-sdk';

const expo = new Expo();

serve(async (req) => {
  const { user_id, message } = await req.json();

  // 1. Get the user's push token from the database
  // (This requires a 'profiles' table with a 'push_token' column)
  const { data: profile, error } = await supabaseAdmin
    .from('profiles')
    .select('push_token')
    .eq('id', user_id)
    .single();

  if (error || !profile || !Expo.isExpoPushToken(profile.push_token)) {
    console.error("Invalid or missing push token for user:", user_id);
    return new Response("Error: Cannot send notification.", { status: 500 });
  }

  // 2. Create the notification message
  const messages = [{
    to: profile.push_token,
    sound: 'default',
    body: message,
    data: { withSome: 'data' }, // Optional data to send with notification
  }];

  // 3. Send the notification
  const chunks = expo.chunkPushNotifications(messages);
  // ... (handle sending chunks and getting tickets) ...

  return new Response("Notification sent.", { status: 200 });
});
```

## 3. Client-Side Implementation (Expo)

*   **Permissions:** The app will need to request permission from the user to send push notifications.
*   **Token Management:** Upon granting permission, the app will get the Expo push token and save it to the user's profile in the Supabase database.
*   **Listeners:** The app will set up listeners to handle notifications that are received while the app is in the foreground or background.

## 4. Next Steps

*   Create the `profiles` table with a `push_token` column.
*   Implement the permission request flow in the Expo app.
*   Develop and deploy the `send-notification` Edge Function.
*   Set up the database trigger to invoke the function on relevant events.
# Decision Log: Notifications Setup

## Table of Contents
- [1. Goal](#1-goal)
- [2. Technical Strategy](#2-technical-strategy)
- [3. Database Trigger Setup](#3-database-trigger-setup)
- [4. Client-Side Implementation (Expo)](#4-client-side-implementation-expo)
- [5. Next Steps](#5-next-steps)

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

## 3. Database Trigger Setup

To invoke the Edge Function automatically, we will create a trigger on the `shopping_list_items` table. The trigger will fire after a new item is inserted, calling a function that then invokes our Edge Function.

```sql
-- 1. Create a function to be called by the trigger
CREATE OR REPLACE FUNCTION handle_new_shopping_item()
RETURNS TRIGGER AS $$
DECLARE
  -- Variables to hold user info
  list_owner_id UUID;
  -- Add more variables for all list members if needed
BEGIN
  -- Get the owner of the list to notify them
  SELECT owner_id INTO list_owner_id
  FROM shopping_lists
  WHERE id = NEW.list_id;

  -- Invoke the Supabase Edge Function
  -- We pass the ID of the user to notify and a custom message
  PERFORM net.http_post(
    url:='https://<project_ref>.supabase.co/functions/v1/send-notification',
    headers:='{"Content-Type": "application/json", "Authorization": "Bearer <supabase_service_role_key>"}'::jsonb,
    body:=('{"user_id": "' || list_owner_id || '", "message": "A new item was added to your list!"}')::jsonb
  );

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2. Create the trigger that fires the function
CREATE TRIGGER on_new_shopping_item_trigger
AFTER INSERT ON shopping_list_items
FOR EACH ROW
EXECUTE FUNCTION handle_new_shopping_item();

```
*(Note: This is a simplified example notifying only the list owner. A more robust solution would iterate through all members of a shared list.)*

## 4. Client-Side Implementation (Expo)

The Expo app needs to be configured to handle push notifications.

1.  **Request Permissions**: When the app starts, or at a logical point in the user flow, we must ask the user for permission to send notifications.

    ```javascript
    async function registerForPushNotificationsAsync() {
      let token;
      // ... (permission checks for iOS and Android) ...
      
      token = (await Notifications.getExpoPushTokenAsync()).data;
      console.log(token);
      
      // Save the token to the user's profile in Supabase
      const { error } = await supabase
        .from('profiles')
        .update({ push_token: token })
        .eq('id', supabase.auth.user().id);

      return token;
    }
    ```

2.  **Handle Incoming Notifications**: We need to set up event listeners to decide what to do when a notification is received.

    *   `Notifications.addNotificationReceivedListener`: Fires when a notification is received while the app is in the **foreground**.
    *   `Notifications.addNotificationResponseReceivedListener`: Fires when a user **taps on** a notification (works for foreground, background, or killed app).

## 5. Next Steps

*   Create a `profiles` table that includes a `push_token` text field.
*   Implement the permission request flow and token storage in the Expo app.
*   Deploy the `send-notification` Edge Function and the database trigger via a Supabase migration.
*   Write an integration test to verify the end-to-end notification flow.
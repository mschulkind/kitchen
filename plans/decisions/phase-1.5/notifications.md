# Decision Log: Notifications Setup

## Table of Contents
- [1. Goal](#1-goal)
- [2. Technical Strategy](#2-technical-strategy)
- [3. Database Trigger Setup](#3-database-trigger-setup)
- [4. Client-Side Implementation (Expo)](#4-client-side-implementation-expo)
- [5. Next Steps](#5-next-steps)

This document describes the plan for implementing push notifications to alert users of relevant activity.

*   **Phase:** 1.5
*   **Status:** Completed (2025-09-18: Expanded triggers/functions for multi-user, Expo handling, UX/TDD; integrated with auth profiles and realtime)
*   **Owner:** A.I. Assistant

## 1. Goal

To proactively inform users about important events within the app, such as when a collaborator updates a shared shopping list or a meal plan is updated. This enhances engagement and the collaborative experience.

## 2. Technical Strategy

We will use a combination of **Supabase Edge Functions** and the **Expo Notifications** library to deliver push notifications. Ties to auth-and-presence.md for user targeting (via profiles.push_token) and realtime-integration.md for event-driven triggers on DB changes (e.g., INSERT/UPDATE via postgres_changes, but use DB triggers for reliability).

### Architecture:
1.  **Database Triggers:** A Postgres trigger will be placed on key tables (e.g., `shopping_list_items`, `inventory_items`, `meal_plans`).
2.  **Edge Function Invocation:** When a relevant change occurs (e.g., a new item is added to a shared list), the trigger will invoke a Supabase Edge Function.
3.  **Function Logic:** The Edge Function will query memberships (from auth RLS) to determine recipients, customize message.
4.  **Push Notification Service:** The function will send to Expo's service; handle receipts/tickets for delivery tracking.
5.  **Client-Side Handling:** Expo app receives via library, handles foreground/background/killed states with deep links to updated resource.

### API Sketch (Edge Function):
```typescript
// supabase/functions/send-notification/index.ts
import { serve } from "https://deno.land/std@0.131.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';
import { Expo } from 'expo-server-sdk';

const supabaseAdmin = createClient(Deno.env.get('SUPABASE_URL')!, Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!);
const expo = new Expo();

serve(async (req) => {
  const { resource_type, resource_id, event_type, actor_id } = await req.json(); // e.g., {resource_type: 'shopping_list', resource_id: 'abc', event_type: 'insert', actor_id: 'user123'}

  // 1. Get members to notify (exclude actor)
  let membersQuery = supabaseAdmin.from('resource_memberships').select('user_id, role').eq('resource_id', resource_id).eq('resource_type', resource_type);
  const { data: members } = await membersQuery;

  const messages = [];
  for (const member of members.filter(m => m.user_id !== actor_id)) {
    // Get push token from profiles
    const { data: profile } = await supabaseAdmin.from('profiles').select('push_token, name').eq('id', member.user_id).single();
    if (profile && Expo.isExpoPushToken(profile.push_token)) {
      let message = '';
      switch (event_type) {
        case 'insert': message = `${actor_name} added an item to the shared ${resource_type}.`; break;
        case 'update': message = `${actor_name} updated the ${resource_type}.`; break;
        // Add more
      }
      messages.push({
        to: profile.push_token,
        sound: 'default',
        title: 'Kitchen App Update',
        body: message,
        data: { resource_type, resource_id, deep_link: `app://shared/${resource_type}/${resource_id}` }
      });
    }
  }

  if (messages.length === 0) return new Response('No recipients', { status: 200 });

  // Send in chunks
  const chunks = expo.chunkPushNotifications(messages);
  const tickets = [];
  for (const chunk of chunks) {
    const ticketChunk = await expo.sendPushNotificationsAsync(chunk);
    tickets.push(...ticketChunk);
  }

  // Handle receipts later via cron or webhook
  console.log('Tickets:', tickets);

  return new Response('Notifications sent', { status: 200 });
});
```

## 3. Database Trigger Setup

To invoke the Edge Function automatically, we will create triggers on key tables. Use pg_net extension for http_post; notify all members via query.

### shopping_list_items (expanded for members)
```sql
-- Function to notify all members (exclude actor if known)
CREATE OR REPLACE FUNCTION handle_shopping_item_change()
RETURNS TRIGGER AS $$
DECLARE
  resource_id UUID := NEW.list_id;
  actor_id UUID := COALESCE(NEW.created_by, NEW.updated_by); -- Assume fields for audit
  payload JSONB;
BEGIN
  payload := jsonb_build_object(
    'resource_type', 'shopping_list',
    'resource_id', resource_id,
    'event_type', TG_OP::text,  -- INSERT, UPDATE, DELETE
    'actor_id', actor_id
  );

  PERFORM net.http_post(
    url:='https://<project_ref>.supabase.co/functions/v1/send-notification',
    headers:='{"Content-Type": "application/json", "Authorization": "Bearer <service_role>"}'::jsonb,
    body:=payload
  );

  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Trigger
CREATE TRIGGER on_shopping_item_change_trigger
AFTER INSERT OR UPDATE OR DELETE ON shopping_list_items
FOR EACH ROW EXECUTE FUNCTION handle_shopping_item_change();
```

### inventory_items Trigger
Similar to above, for shared inventory changes (e.g., quantity update after shopping).
```sql
-- Adapt function for inventory: resource_type='inventory', filter on inventory_id
CREATE TRIGGER on_inventory_item_change_trigger
AFTER INSERT OR UPDATE OR DELETE ON inventory_items
FOR EACH ROW EXECUTE FUNCTION handle_inventory_change();  -- Separate or shared function
```

### meal_plans Trigger
For plan updates (e.g., recipe added).
```sql
CREATE TRIGGER on_meal_plan_change_trigger
AFTER INSERT OR UPDATE OR DELETE ON meal_plans
FOR EACH ROW EXECUTE FUNCTION handle_meal_plan_change();  -- Notify members of plan_id
```

Deploy via Supabase migration; test with RLS to ensure triggers respect policies.

## 4. Client-Side Implementation (Expo)

The Expo app needs to be configured to handle push notifications.

1.  **Request Permissions**: On app start or profile setup.
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

2.  **Handle Incoming Notifications**: Set up listeners for all states; deep link to resource on tap.
   ```javascript
   import * as Notifications from 'expo-notifications';
   import * as Linking from 'expo-linking';

   // On app start
   Notifications.addNotificationReceivedListener(notification => {
     // Foreground: Show in-app alert or badge
     if (notification.request.content.data.deep_link) {
       Alert.alert('Update Available', notification.request.content.body, [
         { text: 'View Now', onPress: () => Linking.openURL(notification.request.content.data.deep_link) }
       ]);
     }
   });

   Notifications.addNotificationResponseReceivedListener(response => {
     // Tap: Background/killed - deep link to resource
     const { deep_link } = response.notification.request.content.data;
     if (deep_link) Linking.openURL(deep_link);  // e.g., navigate to shared list
   });

   // Handle receipt errors (for retries)
   Notifications.setNotificationHandler({
     handleNotification: async () => ({ shouldShowAlert: true, shouldPlaySound: true, shouldSetBadge: false })
   });
   ```

3.  **Token Refresh**: On app resume, re-register token if expired; update profiles table.

## 5. User Feedback & UX (Mobile Focus)
- **Alert Examples**: "John added 'Apples' to the shopping list" with tap to open list; "Sarah updated inventory—check quantities" for realtime tie-in.
- **Permissions UX**: On first launch, modal: "Enable notifications for collab updates?" with big Allow button; fallback to in-app banners if denied.
- **Offline/Queued**: If offline, queue notification intent; send on sync with "2 updates waiting" badge.
- **Customization**: User prefs in profiles (e.g., notify_on_add: true); respect Do Not Disturb via Expo.

## 6. TDD: Testing Notifications
- **Integration Test (e.g., Supabase + Expo mock)**: Simulate DB insert, assert Edge Function call, mock Expo send, verify receipt.
  ```javascript
  test('trigger sends notification to members on insert', async () => {
    // Mock supabaseAdmin insert to shopping_list_items
    await supabase.from('shopping_list_items').insert({ list_id: 'test', name: 'Milk' });
    // Assert http_post called with correct payload
    expect(mockHttpPost).toHaveBeenCalledWith(expect.objectContaining({ body: { user_id: 'member1', message: expect.stringContaining('added') } }));
  });

  // Client: Mock Notifications listener, assert deep link on response
  test('handles notification tap to open resource', async () => {
    const mockResponse = { notification: { request: { content: { data: { deep_link: 'app://shared/list/abc' } } } } };
    Notifications.addNotificationResponseReceivedListener(mockResponse);
    expect(Linking.openURL).toHaveBeenCalledWith('app://shared/list/abc');
  });
  ```

Aim for end-to-end with Detox for mobile permission flows.

## 5. Next Steps
*   Add push_token to profiles data model in design-system.md.
*   Deploy Edge Function and triggers via Supabase CLI.
*   Implement Expo listeners and token management in app.
*   Test full flow: Insert → Trigger → Push → Deep link.
*   Integrate with ux-flow.md for notification handling screens.
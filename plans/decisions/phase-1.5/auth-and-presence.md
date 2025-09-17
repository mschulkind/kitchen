# Decision Log: User Authentication & Presence

This document outlines the strategy for implementing user authentication and real-time presence indicators.

*   **Phase:** 1.5
*   **Status:** Scoping
*   **Owner:** A.I. Assistant

## 1. Goal

To provide a secure and clear way for users to sign in, manage their accounts, and see who else is currently active or collaborating with them on shared resources like shopping lists.

## 2. Authentication Strategy

We will use **Supabase Auth**, leveraging its tight integration with the Supabase database and client SDKs. This simplifies development and provides a robust, secure authentication system out-of-the-box.

### Key Features:

*   **Authentication Methods:** We will initially support email/password sign-up and login. Social providers (e.g., Google, Apple) can be added later with minimal effort.
*   **Session Management:** Supabase's client libraries handle session management, including token storage and refresh, which is crucial for a good PWA experience.
*   **Security:** Row Level Security (RLS) policies will be enforced in the database to ensure users can only access their own data or data explicitly shared with them.

### API Sketch (Authentication):

```javascript
// Sign up a new user
const { data, error } = await supabase.auth.signUp({
  email: 'example@email.com',
  password: 'example-password'
});

// Sign in an existing user
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'example@email.com',
  password: 'example-password'
});
```

## 3. Presence Strategy

Supabase's built-in **Presence** feature will be used to track user online status. This allows us to build UI features that show who is currently viewing or editing a shared list.

### Key Features:

*   **Real-time Tracking:** The client will track its online status and broadcast it to a shared channel.
*   **UI Indicators:** The UI will display avatars or indicators for users who are currently active in a shared context.

### API Sketch (Presence):

```javascript
const presenceChannel = supabase.channel('shared-list-presence', {
  config: {
    presence: {
      key: 'user-id-abc', // A unique key for the user
    },
  },
});

presenceChannel.on('presence', { event: 'sync' }, () => {
  const newState = presenceChannel.presenceState();
  console.log('Current users online:', newState);
  // Update UI to show online users
});

presenceChannel.subscribe(async (status) => {
  if (status === 'SUBSCRIBED') {
    const status = await presenceChannel.track({ online_at: new Date().toISOString() });
    console.log('Tracked status:', status);
  }
});
```

## 4. UI/UX Considerations

### Authentication Flow:
*   **Screens**: Simple, clean screens for Sign Up, Login, and Forgot Password.
*   **Social Login**: Buttons for Google and Apple will be included for a single-tap sign-in option.
*   **User Avatars**: Users can upload a profile picture, which will be used for presence indicators. A default avatar will be assigned on sign-up. Big avatar buttons will be used for inviting users to collaborate.

### Presence Indicators:
*   In a shared context (like a shopping list), the avatars of currently active users will be displayed at the top of the screen.
*   A subtle animation or a green dot on the avatar will indicate that the user is online.
*   If a user is actively typing or editing, a "..." indicator could appear next to their avatar.

## 5. Row Level Security (RLS) Policies

RLS is critical for ensuring users can only access data they own or have been granted access to. The following policies will be implemented:

### Example: `shopping_lists` Table
Users can only see lists they have created or are a member of.

```sql
-- Policy: Allow users to see lists they are members of.
CREATE POLICY "Enable read access for list members"
ON public.shopping_lists FOR SELECT
USING (
  auth.uid() IN (
    SELECT user_id FROM list_memberships WHERE list_id = shopping_lists.id
  )
);

-- Policy: Allow users to create new lists.
CREATE POLICY "Enable insert for authenticated users"
ON public.shopping_lists FOR INSERT
WITH CHECK (auth.role() = 'authenticated');

-- Policy: Allow list owners to update their lists.
CREATE POLICY "Enable update for list owners"
ON public.shopping_lists FOR UPDATE
USING (auth.uid() = owner_id);

```
*(Note: This requires a `list_memberships` table linking `user_id` and `list_id`, and an `owner_id` on the `shopping_lists` table.)*

Similar policies will be created for `shopping_list_items`, `meal_plans`, `pantry_items`, and other user-specific data tables.

## 6. Next Steps

*   Design the UI mockups for the authentication screens.
*   Implement the RLS policies for all relevant tables in a Supabase migration script.
*   Build the frontend components for the login and sign-up flows.
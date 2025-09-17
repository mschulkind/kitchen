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

## 4. Next Steps

*   Design the UI for login, sign-up, and profile management.
*   Define the UI for displaying presence indicators.
*   Implement RLS policies for all relevant tables.
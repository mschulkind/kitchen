# Decision: User Authentication &amp; Presence

## Table of Contents

- [Proposal](#proposal)
- [Decision](#decision)
- [Implementation Details](#implementation-details)

## Proposal

Based on the project's mobile-first nature and reliance on the Supabase stack, the following approach is proposed for user authentication and presence tracking:

### 1. Authentication Method

**Recommendation:** Implement **Google Social Login** exclusively via Supabase Auth.

- **Rationale:**
  - **Simplicity:** Focusing on a single, low-friction authentication method simplifies the user experience and reduces development overhead.
  - **Mobile-First:** Social logins are ideal for mobile devices, minimizing typing and accelerating user onboarding.
  - **Profile Data:** Google login can pre-fill user profile information, such as name and avatar, which is useful for the collaborative features of the app.

### 2. Presence Tracking

**Recommendation:** Utilize **Supabase Realtime channels** for presence tracking.

- **Rationale:**
  - **Efficiency:** This leverages the existing real-time connection already required for data synchronization, avoiding the need for a separate presence system.
  - **Simplicity:** The Supabase client SDK has a straightforward API for tracking and broadcasting user presence within a channel.
  - **Immediate Feedback:** Provides the instant "online" indicators needed for a collaborative environment, as specified in the UX tie-in notes.

## Decision

**Approved:** The project will proceed with the following implementations:

1. **Authentication:** User authentication will be handled exclusively through **Google Social Login** using Supabase Auth. Email/Password authentication will not be implemented.
2. **Presence Tracking:** User presence will be tracked using **Supabase Realtime channels**.

This decision prioritizes a streamlined, mobile-first user experience and leverages the integrated capabilities of the Supabase stack for rapid development.

## Implementation Details

### Authentication API Sketch

```typescript
// Google Social Login (OAuth)
const { data, error } = await supabase.auth.signInWithOAuth({
  provider: 'google',
});
```

### Presence Tracking API Sketch

```typescript
const channel = supabase.channel('shopping_list:123', {
  config: {
    presence: {
      key: 'user-id-abc', // Unique key for the user
    },
  },
});

channel.on('presence', { event: 'sync' }, () => {
  const presenceState = channel.presenceState();
  console.log(presenceState); // Shows all users currently in the channel
});

await channel.subscribe(async (status) => {
  if (status === 'SUBSCRIBED') {
    const status = await channel.track({ online_at: new Date().toISOString() });
    console.log(status); // 'ok'
  }
});

# Tech Stack Rules

For generic LLM integration guidelines, see [.kilocode/rules/library/llm-integration.md](.kilocode/rules/library/llm-integration.md).

- **Frontend**: React Native with Expo for cross-platform mobile app (iOS/Android), focusing on touch-friendly UI (big buttons, simple gestures for shared lists).
- **Backend/Database**: Supabase (PostgreSQL with realtime subscriptions via WebSockets for instant multiuser sync on meal plans, inventory, shopping lists).
- **Realtime Collaboration**: Supabase for live updates (e.g., checkmarks on shared checklists propagate instantly); support multiuser with integrated auth (email/social logins), presence tracking (online indicators), and role-based permissions (owner/editor/viewer).
- **Auth & Security**: Supabase Auth for user management and invites; row-level security for shared resources.
- **Offline/Optimistic Updates**: Supabase client SDK for mobile offline handling (queue changes, sync on reconnect with simple conflict alerts).
- **Notifications**: Expo Notifications triggered by Supabase Edge Functions for change alerts (e.g., "Collaborator added item").
- **Other Tools**: Git for version control; emphasize modern best practices like containerization (Docker) if deployment requires it.
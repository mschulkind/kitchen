# Tech Design Rules

## Table of Contents
- [Tech Stack](#tech-stack)
- [Mobile-First Principles](#mobile-first-principles)

## Tech Stack

- **Frontend**: React Native with Expo for cross-platform mobile app (iOS/Android), focusing on touch-friendly UI (big buttons, simple gestures for shared lists).
- **Backend/Database**: Supabase (PostgreSQL with realtime subscriptions via WebSockets for instant multiuser sync on meal plans, inventory, shopping lists).
- **Realtime Collaboration**: Supabase for live updates (e.g., checkmarks on shared checklists propagate instantly); support multiuser with integrated auth (email/social logins), presence tracking (online indicators), and role-based permissions (owner/editor/viewer).
- **Auth & Security**: Supabase Auth for user management and invites; row-level security for shared resources.
- **Offline/Optimistic Updates**: Supabase client SDK for mobile offline handling (queue changes, sync on reconnect with simple conflict alerts).
- **Notifications**: Expo Notifications triggered by Supabase Edge Functions for change alerts (e.g., "Collaborator added item").
- **Other Tools**: Git for version control; emphasize modern best practices like containerization (Docker) if deployment requires it.

## Mobile-First Principles

- **UX Focus**: Design for mobile/on-the-go use with large touch targets (min 44x44px), minimal navigation (e.g., bottom tabs or gesture-based), and simple, intuitive interfaces that "just work."
- **Responsiveness**: Use Tailwind's mobile-first breakpoints; test on various screen sizes. Prioritize offline capability (e.g., service workers for PWA, local storage for inventory).
- **Accessibility**: Ensure high contrast, semantic HTML in React, and keyboard navigation support. Flows like ingredient verification should use categorical checklists for quick scanning.
- **Performance**: Optimize for low latency; lazy-load non-essential components, use efficient data fetching (e.g., TanStack Query for React).
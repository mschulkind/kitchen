# Mobile-First Principles
- **UX Focus**: Design for mobile/on-the-go use with large touch targets (min 44x44px), minimal navigation (e.g., bottom tabs or gesture-based), and simple, intuitive interfaces that "just work."
- **Responsiveness**: Use Tailwind's mobile-first breakpoints; test on various screen sizes. Prioritize offline capability (e.g., service workers for PWA, local storage for inventory).
- **Accessibility**: Ensure high contrast, semantic HTML in React, and keyboard navigation support. Flows like ingredient verification should use categorical checklists for quick scanning.
- **Performance**: Optimize for low latency; lazy-load non-essential components, use efficient data fetching (e.g., TanStack Query for React).
# Decision: Detail Meal Planning Verification Flow

## Overview

This decision defines the user flow for verifying and refining LLM-generated meal plans before finalizing shopping lists or inventory adjustments. The flow ensures accuracy, personalization, and ease in a mobile context, integrating realtime sync for collaborators. Key elements: review suggestions, edit items, approve changes, handle errors (e.g., unavailable ingredients).

## Options

- **Option 1: Simple Approve/Reject Flow**
  - Present meal plan as a card/list with key details (ingredients, steps, nutrition).
  - User taps "Approve" to add to calendar/shopping, or "Reject" to regenerate; minimal editing.

- **Option 2: Interactive Edit Flow**
  - Allow inline edits (e.g., swap ingredients via dropdown, adjust portions with sliders).
  - Multi-step modal: Review → Edit → Preview shopping impact → Confirm.

- **Option 3: Collaborative Review Flow**
  - For multiuser: Show changes with author attribution; vote/approve for shared plans.
  - Include chat-like comments or quick reactions; sync via Supabase realtime.

## Pros/Cons

- **Simple Approve/Reject**:
  - Pros: Fast for quick users; low cognitive load; suitable for on-the-go.
  - Cons: Limited customization; may lead to suboptimal plans if rejects are frequent.

- **Interactive Edit**:
  - Pros: Empowers user control; better for personalization (e.g., allergy swaps).
  - Cons: Higher interaction complexity; potential for errors in mobile input.

- **Collaborative Review**:
  - Pros: Enhances multiuser experience; reduces conflicts via consensus.
  - Cons: Adds latency for sync; overkill for solo use; requires auth integration.

## Questions for User

- Preferred level of interactivity: Quick approve or detailed editing (e.g., sliders for portions)?
- Integration with shopping: Auto-add unconfirmed items to list, or require explicit approval?
- For multiuser: Include voting, comments, or just notifications for changes?
- Error handling: Regenerate on reject, or fallback to manual entry?

## Next Steps

Choose flow and create Mermaid sequence diagrams; update ux-flow.md with details and design-system.md for UI components. Reference: [plans/ux-flow.md](../ux-flow.md), [plans/design-system.md](../design-system.md), [plans/brief.md](../brief.md).

*Decision Pending - Awaiting User Input*

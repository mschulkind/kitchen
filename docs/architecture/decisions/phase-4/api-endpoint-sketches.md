# Decision: Create API Endpoint Sketches

## Overview

This decision sketches REST API endpoints for the backend (FastAPI), supporting features like meal planning, inventory management, and shopping lists. Endpoints will integrate with Supabase for auth and realtime, ensuring secure, efficient PWA interactions. Focus on mobile-optimized responses (e.g., JSON with minimal payloads).

## Options

- **Option 1: Standard REST Endpoints**
  - GET /inventory, POST /inventory/item, PUT /inventory/{id}, DELETE /inventory/{id}
  - GET /meal-plans?date=YYYY-MM-DD, POST /meal-plans
  - GET /shopping-lists, POST /shopping-lists/item, PATCH /shopping-lists/{id}/check

- **Option 2: Resource-Based with Filtering**
  - /api/v1/resources/inventory?filter[location]=fridge&sort=expiry
  - /api/v1/meal-plans/generate (POST with body: {pantry_items, prefs})
  - Include query params for pagination, search; realtime via WebSocket separate.

- **Option 3: Hybrid with RPC for Complex Ops**
  - REST for CRUD, RPC for optimizations (e.g., POST /optimize-meal {ingredients} → LLM call).
  - Use FastAPI dependencies for auth (Supabase JWT).

## Pros/Cons

- **Standard REST**:
  - Pros: Familiar, cacheable; easy to implement with FastAPI routers.
  - Cons: Can lead to over-fetching; more endpoints for complex queries.

- **Resource-Based**:
  - Pros: Flexible querying; reduces roundtrips for mobile.
  - Cons: URL complexity; potential security risks if filters not sanitized.

- **Hybrid RPC**:
  - Pros: Efficient for AI features; clear separation of concerns.
  - Cons: Less standardized; harder to document/test uniformly.

## Questions for User

- Use REST only or include RPC for LLM integrations?
- Auth per endpoint (e.g., all require JWT, or public for read-only)?
- Response format: Full objects or lean (e.g., ids only for lists)?
- Error handling: Standard HTTP codes or custom JSON errors?

## Next Steps

Outline 10-15 key endpoints with methods, params, responses; add to design-system.md. Reference: [plans/design-system.md](../design-system.md), [plans/ux-flow.md](../ux-flow.md), [plans/brief.md](../brief.md).

*Decision Pending - Awaiting User Input*

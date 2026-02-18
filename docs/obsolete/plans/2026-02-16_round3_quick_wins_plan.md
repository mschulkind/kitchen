# 🐋 Round 3: Quick Wins Implementation Plan

> **Date**: 2026-02-16
> **Goal**: Implement all "quick win" features identified in QA Round 2 that don't require user input or external dependencies.

## Problem Statement

QA Round 2 revealed that 38/58 scenarios pass, but many failures are due to missing frontend wiring rather than missing backend logic. Six features can be completed without any user input, API keys, or infrastructure changes.

## Scope — What We're Building

### 1. Recipe Edit & Delete UI (KNOWN-04 → RCP-06, RCP-07)
Backend PATCH/DELETE endpoints exist and are fully implemented. Need:
- Delete button on recipe detail page with confirmation
- Edit button on recipe detail page → edit form (reuse `new.tsx` pattern)
- Wire mutations to API endpoints

### 2. Check-Stock "Add to Shopping List" Fix (KNOWN-03 → DEL-04)
Missing `household_id` in the Supabase insert. One-line fix + null guard.

### 3. Cooking Mode Mise-en-Place (COOK-02)
Backend endpoint `/cooking/mise-en-place/{recipe_id}` exists and returns prep tasks.
The "Ingredients" button in cook.tsx has a `TODO` comment. Need:
- Fetch mise-en-place data from API
- Show as a modal/bottom sheet checklist over cooking mode

### 4. Store Sorter → Shopping List Integration (P3B → SHOP-07)
Backend `StoreSorter` is complete with 14-aisle mapping. Frontend already groups by hardcoded categories. Need:
- New API endpoint: `GET /shopping/sorted/{list_id}`
- Frontend: replace hardcoded `CATEGORY_ORDER` with API-driven aisle groups

### 5. Settings User Display Fix (KNOWN-06 → SETT-01)
Hardcoded "Guest User" text. Fix: pull display name from Supabase auth session.

### 6. Planner Manual Meal Assignment (PLN-03)
Service method `update_slot()` exists but has no REST endpoint. Frontend `add.tsx` uses direct Supabase calls. Need:
- New API endpoint for slot assignment
- Wire frontend to use API

## Out of Scope
- Supabase Realtime (infra — needs user input)
- Vision/Image features (needs API key)
- JWT auth integration (design decision)
- Voice frontend (lower priority)
- Recipe URL import (needs internet)

## Open Questions
None — all features here are self-contained with existing backends.

# Project Brief: Personalized Dinner &amp; Shopping App

***

## Table of Contents

- [Project Summary](#project-summary)
- [Key Features &amp; User Experience](#key-features--user-experience)
- [Technical Architecture](#technical-architecture)
- [Scope and Target Audience](#scope-and-target-audience)
- [Development Strategy: Multi-Platform via Code Sharing](#development-strategy-multi-platform-via-code-sharing)

***

## Project Summary

This document outlines a preliminary design for a *personal-use app* to manage dinner recipes, meal planning, and grocery shopping. The primary goal is to create a **highly usable, efficient tool** that streamlines the process of cooking, tailored to the user's specific tastes, pantry inventory, and gardening habits.

***

## Key Features &amp; User Experience

### Intelligent Meal Planning

The app will generate a coherent **meal plan** for a set number of days (e.g., 4 days) by selecting recipes that are efficient from an ingredient standpoint. The app will prioritize recipes that *share ingredients*, *use up garden surpluses*, and *incorporate leftovers* (e.g., roast chicken one night, chicken soup the next).

### Dynamic Inventory Tracking

An internal data model will track **pantry staples** and **fresh garden produce**. The recipe selection algorithm will heavily favor recipes that use ingredients the user *already has on hand*, giving extra weight to common staples like milk and butter.

### Intuitive Verification Interface

A core user experience will be the **ingredient verification process**. A *"Categorical Checklist" UI* will be implemented, grouping ingredients by their physical location in the kitchen (*Pantry*, *Fridge*, *Freezer*, *Garden*). This makes it easy for the user to confirm what they already have on hand.

### Optimized Shopping List

After verification, the app will generate a final, **definitive shopping list**. This list will be sorted by *average grocery store layout* (e.g., Produce, Dairy, Meat) to optimize the in-store shopping trip. The final list will only show items the user needs to purchase.

***

## Technical Architecture

### Backend

The backend will be responsible for the **core logic**, including recipe selection, inventory management, and shopping list generation. It will include a `PantryItem` data model and a `ShoppingListItem` data model.

### LLM Integration

An **LLM agent** will be integrated into the backend to provide dynamic capabilities, such as suggesting new recipes based on current ingredients, offering recipe variety, and customizing recipes on the fly.

This preliminary design document captures the core vision for the app, emphasizing **usability** and **efficiency** as the primary design drivers.

***

## Scope and Target Audience

This application is designed for **private use** by a small number of users. The initial target platforms are a ***desktop web application*** (for testing and usage on Linux) and an ***Android mobile app***. The project will prioritize **code sharing** to maintain a single, unified codebase for both platforms.

***

## Development Strategy: Multi-Platform via Code Sharing

To accommodate the need for both a testable desktop/web application and a native Android app, we will adopt a **multi-platform strategy** centered around code sharing with `react-native-web`.

1. ***Shared Core Development:*** The project will begin by developing a **shared core** of React components and business logic. This core will be written in a platform-agnostic way, allowing it to run on both the web and native Android.
2. ***Web-First for Testing:*** A **web application** will be the first target output. This will serve as the primary platform for development, testing, and light usage on a Linux PC. It will be built from the shared core components and can be run in any modern web browser.
3. ***Android Application Wrapper:*** Once the web application and its core components are stable, they will be wrapped in a **React Native shell** to create the native Android application. This approach ensures that the vast majority of the code is shared, reducing development time and ensuring consistency between the two platforms.
4. ***Deployment:*** The web application can be deployed on any standard web server, and the Android application will be distributed via a side-loadable **APK**.

This strategy provides a clear path for *testing on Linux*, delivers a *native mobile experience*, and creates a *flexible foundation for future platform expansion*.

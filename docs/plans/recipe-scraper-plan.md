# Recipe Scraper Script Plan

> **Fun Fact:** The first known recipe dates back to ancient Mesopotamia around 1750 B.C. It was for a lamb stew! 🍲

This document outlines the plan for creating a Python script to scrape recipes from websites. The script will be resumable, updatable, and provide progress output.

## Phases and Key Features

### Phase 1: Core Scraping Logic

- **Objective:** Build the basic framework for crawling and scraping a single-threaded command-line application.
- **Key Features:**
  - Use `typer` for the command-line interface.
  - Use `firecrawl-local` to scrape recipe content.
  - Add a configuration option for the Firecrawl API endpoint to allow pointing to a self-hosted instance.
  - Add a `--limit` flag to control the number of pages scraped in a single run.
  - Identify and differentiate between collection/index pages and individual recipe pages.
  - Save scraped recipes to a local directory structure, organized by site (e.g., `data/cookwell-com/recipe-name.md`).
  - Basic progress reporting (e.g., "Scraped X of Y pages").

### Phase 2: Resumability and State Management

- **Objective:** Prevent re-scraping already downloaded content.
- **Key Features:**
  - Maintain a local state file (e.g., a SQLite database or JSON file) to track visited URLs.
  - Before scraping a URL, check if it's already in the state file.
  - Add a `--resume` flag to enable this functionality.
  - The state file will store URL, timestamp of last scrape, and a hash of the content to detect changes.

### Phase 3: Update and Concurrency

- **Objective:** Efficiently check for new or updated recipes and speed up scraping.
- **Key Features:**
  - Add an `--update` mode that re-scrapes pages based on certain criteria (e.g., if the page has changed since the last scrape).
  - Use content hashing to detect changes in recipes.
  - Introduce concurrency using Python's `asyncio` and `httpx` to scrape multiple pages at once.
  - Use a library like `rich` to provide detailed, color-coded progress output.

### Phase 4: Advanced Features and Extensibility

- **Objective:** Handle larger sites and make the scraper more robust.
- **Key Features:**
  - Implement filtering to target specific sections of a site (e.g., only scrape URLs matching a certain pattern).
  - Add support for different output formats (e.g., JSON, YAML).
  - Create a plugin system to easily add support for new recipe sites with custom parsing logic.
  - Add robust error handling and retries.

## Mermaid Diagram: Scraper Workflow

```mermaid
graph TD
    A[Start] --> B{URL in state?};
    B -- Yes --> C{--update flag?};
    B -- No --> D[Scrape URL];
    C -- Yes --> E{Content changed?};
    C -- No --> F[Skip];
    E -- Yes --> D;
    E -- No --> F;
    D --> G[Save content];
    G --> H[Update state];
    H --> I[End];
    F --> I;

# Hosting and Deployment

## Table of Contents

- [Primary Hosting Strategy: Self-Hosted on Raspberry Pi](#primary-hosting-strategy-self-hosted-on-raspberry-pi)
- [Local Development Setup](#local-development-setup)
- [Alternative Hosting Options (Cloud)](#alternative-hosting-options-cloud)
- [PWA and Mobile Deployment](#pwa-and-mobile-deployment)
- [CI/CD and Monitoring](#cicd-and-monitoring)
- [Pending Decisions](#pending-decisions)
- [References](#references)

This document outlines the hosting and deployment strategy for the Personalized Dinner & Shopping App, from local development to potential production environments. It focuses on simplicity for personal use while allowing scalability. Reference [design-system.md](design-system.md) for tech stack details and [brief.md](brief.md) for offline-capable goals.

## Primary Hosting Strategy: Self-Hosted on Raspberry Pi

Based on the decision to self-host, the primary deployment target will be a Raspberry Pi running Docker. This approach provides full control over the environment and data.

- **Orchestration**: `docker-compose` will be used to define and manage the multi-container application stack.
- **Application Components**:
  - **Frontend (React/Vite)**: A multi-stage `Dockerfile` will be created to first build the static assets, which are then served by a lightweight web server like Nginx.
  - **Backend (Python/FastAPI)**: A dedicated Docker container running the FastAPI application with `uvicorn`.
  - **Database (Supabase)**: We will leverage the official Supabase Docker images to run the entire Supabase stack (Postgres, GoTrue, Realtime, etc.) locally on the Raspberry Pi. This provides the power of Supabase while keeping all data on-premise.
- **Networking**: All containers will be connected via a shared Docker network. The frontend container's web server will be configured to proxy API requests to the backend container.
- **ARM64 Compatibility**: All Docker images must be compatible with the Raspberry Pi's ARM64 architecture. We will need to verify or build ARM-compatible images for each service.
- **Deployment Workflow**:
  1. Develop and test locally using the Supabase CLI.
  2. Build and tag production-ready Docker images for each service.
  3. Push images to a private registry (or use local builds on the Pi).
  4. Use `docker-compose up -d` on the Raspberry Pi to deploy or update the application.

## Local Development Setup

**Goal**: Quick, reliable local runs for development and testing, emphasizing fast iteration.

- **Backend**:
  - Run with `uvicorn` or `python -m fastapi` (e.g., `uvicorn main:app --reload`).
  - Database: SQLite file in project root (e.g., `app.db`); initialize with migrations if using Alembic.
  - Environment: Use `.env` for secrets (e.g., LLM API keys); load with `python-dotenv`.
  - Ports: Backend on 8000; enable CORS for frontend.

- **Frontend**:
  - Run with `npm run dev` (Vite dev server on port 5173).
  - Proxy API calls to backend (configure in `vite.config.ts`).
  - Database Sync: Use local storage or IndexedDB for offline inventory; sync to backend when online.

- **Full Stack Run**:
  - **Process Management**: Use Overmind (<https://github.com/DarthSim/overmind>) to manage multiple development services in a single terminal session. Overmind provides a tmux-based interface for starting, stopping, and monitoring all services simultaneously.
  - **Procfile**: Create a `Procfile.dev` at the project root with the following processes:

    ```
    frontend: npm run dev
    backend: uvicorn main:app --reload --port 8000
    supabase: supabase start
    ```

  - **Commands**:
    - Install Overmind: `cargo install overmind` (requires Rust/Cargo).
    - Start all services: `overmind start -f Procfile.dev`
    - This will launch the frontend (Vite on port 5173), backend (FastAPI on port 8000), and Supabase local stack in separate panes, allowing easy monitoring and hot-reloading.
  - **Benefits**: Unified control for full-stack development; easy to add more services (e.g., tests, watchers); persists sessions across terminal closes.
  - Testing: Run tests with `pytest` and `vitest`; aim for sub-second suites.
  - PWA: Enable service worker in Vite for offline caching during dev.
  - **Database**: Use the Supabase CLI (`supabase start`) to mirror the self-hosted production environment.

- **Requirements**:
  - Install: `pip install -r requirements.txt` (FastAPI, Pydantic, etc.); `npm install` for frontend.
  - TODO: Create `setup.sh` or `Makefile` for one-command setup.

**Text Setup Flow**:

```text
1. Clone repo & cd into root
2. Install dependencies: pip install -r requirements.txt; npm install
3. Install Overmind: cargo install overmind
4. Start all services: overmind start -f Procfile.dev
5. Access: http://localhost:5173 (frontend proxies to :8000)
6. Test: npm run test:all
```

## Alternative Hosting Options (Cloud)

**Goal**: Optional deployment for access from multiple devices (e.g., phone, home server); prioritize free/low-cost for personal app.

- **Frontend (React/Vite)**:
  - **Vercel**: Ideal for static/SPA hosting; auto-deploys from GitHub. Supports PWA out-of-box.
    - Pros: Fast CDN, preview branches, serverless functions if needed.
    - Cons: Free tier limits; custom domain easy.
  - **Netlify**: Alternative for drag-and-drop or Git integration; good for PWAs.
  - TODO: Decide on env vars for API base URL.

- **Backend (FastAPI)**:
  - **Heroku**: Simple PaaS; free dyno for low-traffic. Use `Procfile` (e.g., `web: uvicorn main:app`).
    - Database: Heroku Postgres add-on (free tier available).
    - Pros: Easy scaling, no server management.
    - Cons: Sleeps after 30min inactivity (wake on request).
  - **DigitalOcean App Platform**: For more control; deploy from Git, auto-builds.
    - Alternative: Render or Railway for similar PaaS.
  - **Serverless**: AWS Lambda or Vercel Functions if breaking into APIs; but overkill for now.

- **Database**:
  - Local: SQLite.
  - Cloud: PostgreSQL on Heroku/Supabase (free tier); migrate schemas with Alembic.
  - TODO: Evaluate data privacy – keep inventory local unless syncing needed.

- **Full Deployment Flow**:
  1. Push to GitHub.
  2. Connect Vercel/Heroku to repo for auto-deploys.
  3. Set env vars (e.g., `DATABASE_URL`, `OPENAI_API_KEY`).
  4. Custom Domain: Optional via Vercel (e.g., dinnerapp.example.com).

## PWA and Mobile Deployment

**Goal**: Enable installable app on mobile for offline use, aligning with on-the-go UX.

- **PWA Setup**:
  - Manifest: `public/manifest.json` with icons, name ("Dinner Planner"), theme colors.
  - Service Worker: Use Vite PWA plugin (`vite-plugin-pwa`) for caching (e.g., cache API responses, recipes).
  - Offline: Fallback to cached inventory/plan; queue LLM calls for reconnect.
  - Install Prompt: Trigger on first visit if criteria met (HTTPS, etc.).

- **Mobile Considerations**:
  - Testing: Chrome DevTools for mobile emulation; Lighthouse for PWA audits.
  - Distribution: Host on Vercel; users add to home screen.
  - Native Alternative: If needed, Capacitor or React Native wrapper (but stick to web for now).
  - TODO: Permissions for notifications (e.g., "Low on staples").

## CI/CD and Monitoring

- **CI**: GitHub Actions for tests on push/PR (run pytest + vitest).
  - Workflow: Lint → Test → Build → Deploy preview.
- **Monitoring**: Basic logging with Sentry (free tier) for errors; track LLM usage.
- **Security**: HTTPS enforced; no auth, but validate inputs.
- TODO: Set up deploy checklist (e.g., backup DB, test offline mode).

## Pending Decisions

- **Primary Hosting**: Vercel + Heroku combo vs. all-in-one (e.g., DigitalOcean).
- **Database Migration**: Tool choice (Alembic vs. manual scripts).
- **Cost Management**: Monitor free tiers; budget for LLM API (~$5/month low use).
- **Scaling**: If app grows, consider Docker for containerization.

## References

- Align with TDD rules in [.kilocode/rules.md](../.kilocode/rules.md).
- UX flows in [ux-flow.md](ux-flow.md) for deployment testing.

TODO: Finalize choices post-prototype; document exact commands in a README.

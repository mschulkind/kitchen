# Hosting and Deployment

This document outlines the hosting and deployment strategy for the Personalized Dinner & Shopping App, from local development to potential production environments. It focuses on simplicity for personal use while allowing scalability. Reference [design-system.md](design-system.md) for tech stack details and [brief.md](brief.md) for offline-capable goals.

## Realtime Hosting Recommendations

Given the realtime multiuser collaboration requirements, hosting must support instant sync across devices while maintaining mobile-first deployment ease and scalability.

**Primary Stack:**
- **Database & Realtime: Supabase**
  - Use Supabase's PostgreSQL with realtime subscriptions (WebSockets) for live updates (e.g., shared inventory changes propagate instantly).
  - Integrated auth and edge functions for handling initial syncs, notifications, and conflict resolution.
  - Offline support via client SDKs for mobile apps—optimistic updates sync on reconnect without user intervention.
  - Setup: Free tier for dev; scales to production with row-level security for multiuser permissions.
  - Mobile Considerations: Supabase JS client works seamlessly with React Native/Expo; low-latency edge network minimizes mobile data usage.

- **Frontend Hosting: Vercel**
  - Deploy React Native/Expo web views or companion web app for desktop collaboration.
  - Serverless functions for backend logic (e.g., invite processing, custom sync hooks if needed beyond Supabase).
  - Automatic deployments from Git; integrates with Supabase for full-stack realtime.
  - Pros: Fast deploys, global CDN for low-latency realtime; free for small teams.

**CI/CD for Collaborative Development**
- **GitHub Actions or Vercel Pipelines**: Automate testing/deployments on pull requests—essential for multiuser dev (e.g., test realtime sync in CI with simulated users).
  - Steps: Lint/test on PR > Deploy preview branch > Merge to main triggers prod deploy.
  - Include Supabase migrations in CI (e.g., db push on deploy).
- **Version Control Best Practices**: Branch-per-feature for collaborative changes; protect main branch with required reviews.
- **Monitoring**: Vercel Analytics for perf; Supabase logs for realtime events; add Sentry for error tracking in shared sessions.

This setup enables quick iteration on realtime features (e.g., Supabase dashboard for testing subscriptions) without slowing dev speed, while supporting shared use cases like live shopping list edits across mobile devices.

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
  - Scripts: Add `npm run dev:full` to start both (concurrently).
  - Testing: Run tests with `pytest` and `vitest`; aim for sub-second suites.
  - PWA: Enable service worker in Vite for offline caching during dev.

- **Requirements**:
  - Install: `pip install -r requirements.txt` (FastAPI, Pydantic, etc.); `npm install` for frontend.
  - TODO: Create `setup.sh` or `Makefile` for one-command setup.

**Text Setup Flow**:
```
1. Clone repo & cd into root
2. Backend: pip install -r requirements.txt; uvicorn main:app --reload
3. Frontend: npm install; npm run dev
4. Access: http://localhost:5173 (frontend proxies to :8000)
5. Test: npm run test:all
```

## Cloud Hosting Options
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
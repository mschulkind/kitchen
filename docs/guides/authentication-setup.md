# Authentication Setup Guide 🔐

This guide details how to configure **Google Social Login** for the Kitchen App, covering both local development and production (Synology NAS).

## Overview

We use **Supabase Auth** exclusively. User sign-in is handled via OAuth 2.0 with Google. This requires setting up a Google Cloud Project and obtaining a **Client ID** and **Client Secret**, then connecting these to our Supabase instance.

## 1. Google Cloud Console Setup

You need to create a project in Google Cloud to generate the credentials.

### Step 1: Create a Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project dropdown (top left) and select **"New Project"**.
3. Name it `Kitchen-App` (or similar).
4. Click **Create**.

### Step 2: Configure OAuth Consent Screen

1. In the left sidebar, go to **APIs & Services** > **OAuth consent screen**.
2. Select **External** (unless you have a Google Workspace organization and want to restrict it internal-only).
3. Click **Create**.
4. **App Information**:
   - **App Name**: Kitchen App
   - **User Support Email**: Your email.
5. **Developer Contact Information**: Your email.
6. Click **Save and Continue**.
7. **Scopes**: You can skip adding specific scopes for now (the defaults `email`, `profile`, `openid` are usually sufficient).
8. **Test Users**: Add your own email address so you can test logging in during development.

### Step 3: Create Credentials

1. Go to **APIs & Services** > **Credentials**.
2. Click **+ CREATE CREDENTIALS** > **OAuth client ID**.
3. **Application type**: Select **Web application**.
4. **Name**: `Kitchen App Client`.
5. **Authorized JavaScript origins**:
   - *Dev*: `http://localhost:8200`
   - *Prod*: `https://my-kitchen-app.synology.me` (or `http://YOUR_NAS_IP:8081` if using IP)
   - *Supabase Local*: `http://127.0.0.1:54321` (required for local Auth helpers)
6. **Authorized redirect URIs**:
   *This is where Google sends the user back after login. It must match your Supabase Auth callback URL.*

   **For Local Development:**
   - `http://127.0.0.1:54321/auth/v1/callback`

   **For Production (Synology):**
   - If using the standard setup: `http://YOUR_NAS_IP:8000/auth/v1/callback`
   - Or if using a reverse proxy: `https://my-kitchen-app.synology.me/auth/v1/callback`

7. Click **Create**.
8. **Copy** the **Client ID** and **Client Secret**. Save these safely!

## 2. Configure Supabase (Local Dev)

To make this work locally with `npx supabase start`:

1. Open your project's `config.toml` (usually in `supabase/config.toml`) OR use the local Dashboard.
2. If the local dashboard is running (default: `http://localhost:54323`), go to **Authentication** > **Providers**.
3. Find **Google** and enable it.
4. Paste your **Client ID** and **Client Secret**.
5. Save changes.

Alternatively, create a `.env.local` file for your Supabase folder if your setup supports it, but the Dashboard UI is the easiest method for local stacks.

## 3. Configure Supabase (Production / Docker)

For the self-hosted Docker stack on Synology, you pass these credentials as environment variables to the Auth service (GoTrue).

### Update `.env`

Add the following to your production `.env` file (on the NAS):

```ini
# ... existing config ...

# Google Auth
GOTRUE_EXTERNAL_GOOGLE_ENABLED=true
GOTRUE_EXTERNAL_GOOGLE_CLIENT_ID=your_client_id_here
GOTRUE_EXTERNAL_GOOGLE_SECRET=your_client_secret_here
GOTRUE_EXTERNAL_GOOGLE_REDIRECT_URI=https://my-kitchen-app.synology.me/auth/v1/callback
```

*Note: Ensure the `GOTRUE_EXTERNAL_GOOGLE_REDIRECT_URI` matches exactly what you entered in the Google Cloud Console.*

## 4. Troubleshooting

- **Redirect Mismatch Error**: The URL in your browser address bar when the error occurs must match *exactly* one of the "Authorized redirect URIs" in Google Console. Check for `http` vs `https` and trailing slashes.
- **"App not verified" Warning**: This is normal in development until you submit your app for verification. Just click "Advanced" > "Go to Kitchen App (unsafe)" to proceed.
- **Localhost vs 127.0.0.1**: Google treats these as different domains. Supabase local often defaults to `127.0.0.1`. Ensure you use the one your browser is actually visiting.

## 5. Automation & Headless Testing (MCP / CI)

Tools like **Chrome DevTools MCP** (used by AI agents), **Playwright**, and **Puppeteer** run in "headless" environments where interactive Google Login flows (popups, 2FA) are difficult or impossible to automate. Google also actively blocks automated browsers.

To support agents and tests, we implement "Bypass Strategies".

### Strategy A: The "/devlogin" Backdoor (Hardened)

For local development and AI agents, we use a dedicated route `/devlogin`.

1.  **Route**: `src/mobile/app/devlogin.tsx`
2.  **Behavior**:
    *   **Dev Mode**: Presents a login form for the service account (`admin@kitchen.local` / `admin123`).
    *   **Production**: The file is **physically excluded** from the bundle via `metro.config.js` `exclusionList`, making the route 404 and the code non-existent.
3.  **Usage**:
    *   Navigate to `http://localhost:8081/devlogin`.
    *   Click "Authorize Service Account".

**Agent Instruction**: *"If stuck on auth, go to /devlogin and sign in as admin."*

### Strategy B: "Service Account" User (Email/Password)

Even if the app is "Google Only" for real users, enable the **Email/Password** provider in Supabase specifically for automation.

1.  **Setup**:
    *   Enable **Email/Password** provider in Supabase.
    *   Create a user: `bot@kitchen.app` with a strong password.
    *   (Optional) Use PostgreSQL Triggers or RLS to prevent this user from accessing real user data, or restrict Email/Password logins to *only* this specific email.
2.  **Usage**:
    *   Agents/Tests can use `page.fill()` on hidden/dev-only inputs to log in with credentials.
    *   Avoids Google's bot detection entirely.

### Strategy C: Session Injection (CI/Playwright)

For strict E2E testing where you want to test the *application* state without using the UI to log in.

1.  **Mint a Token**: Use `supabase-admin` (server-side) to generate a valid Session JWT for a test user.
2.  **Inject**: Before the test page loads, inject this token into the browser's `localStorage` (key: `sb-<project-ref>-auth-token`).
3.  **Reload**: The Supabase client initializes, finds the valid token, and restores the session immediately.

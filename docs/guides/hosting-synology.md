# Hosting on Synology NAS 🏠

This guide details how to deploy the Kitchen stack to a Synology NAS using Container Manager (Docker).

## Prerequisites

1. **Synology NAS** with Container Manager installed.
2. **SSH Access** enabled (for initial setup/debugging).
3. **Port Forwarding** (Optional): If you want to access it outside your home network (via VPN/Tailscale is recommended instead).

## 1. Directory Setup

On your NAS, create a folder structure (e.g., via File Station or SSH):

```bash
/volume1/docker/kitchen/
├── docker-compose.yml
├── .env
└── infra/
    └── docker/
        └── volumes/
            └── db/  <-- Maps to Postgres data
```

## 2. Configuration (`.env`)

Create a `.env` file in the root directory:

```ini
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure_password_here
POSTGRES_DB=kitchen

# Supabase (Self-Hosted subsets)
SUPABASE_JWT_SECRET=super_long_secret_key_for_tokens
SUPABASE_ANON_KEY=public_anon_key
SUPABASE_SERVICE_ROLE_KEY=service_role_key

# API
API_PORT=8000
ENVIRONMENT=production

# LLM Keys (Get these from your providers)
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
ANTHROPIC_API_KEY=...
```

## 3. Docker Compose

Copy the `infra/docker/docker-compose.yml` from this repo to your NAS.

> **Note**: Ensure the volume paths in `docker-compose.yml` match your NAS paths if you aren't using relative paths.

## 4. Deployment

### Method A: Via Container Manager UI

1. Open **Container Manager**.
2. Go to **Project** -> **Create**.
3. Name: `kitchen`.
4. Path: `/volume1/docker/kitchen`.
5. Source: "Use existing docker-compose.yml".
6. Click **Next** -> **Done**.

### Method B: Via SSH (Recommended for updates)

```bash
ssh user@synology-ip
cd /volume1/docker/kitchen
sudo docker-compose pull
sudo docker-compose up -d
```

## 5. Network Access

- **Web App**: `http://NAS_IP:8081`
- **API**: `http://NAS_IP:8000`
- **Database**: `NAS_IP:5432`

## 7. External Access & TLS (HTTPS) 🔒

To access the app securely from outside your home (or just to stop browser warnings), use Synology's built-in tools.

### Step 1: DDNS (Dynamic DNS)

If you don't have a static IP, set up a domain name.

1. **Control Panel** > **External Access** > **DDNS**.

2. **Add**: Select provider (e.g., `Synology`, `DuckDNS`, `Google`).

3. Hostname: e.g., `my-kitchen-app.synology.me`.

4. Test Connection & Save.

### Step 2: SSL Certificate (Let's Encrypt)

1. **Control Panel** > **Security** > **Certificate**.

2. **Add** > **Add a new certificate** > **Get a certificate from Let's Encrypt**.

3. Domain name: `my-kitchen-app.synology.me`.

4. Email: Your email.

5. **Apply**. Synology will auto-renew this for you.

### Step 3: Reverse Proxy

Map the HTTPS domain to your local Docker ports.

1. **Control Panel** > **Login Portal** > **Advanced** > **Reverse Proxy**.

2. **Create** Rule for Frontend:

    - **Source**:

        - Protocol: `HTTPS`

        - Hostname: `my-kitchen-app.synology.me`

        - Port: `443`

    - **Destination**:

        - Protocol: `HTTP`

        - Hostname: `localhost`

        - Port: `8081` (The Expo Web Port)

3. **Create** Rule for API (Optional/Advanced):

    - *Note*: If your frontend calls the API via `/api`, you might need a custom Nginx config or Traefik.

    - *Simpler*: Just map the API to a different subdomain (`api-kitchen.synology.me`) or a different port if needed.

    - *Recommended*: Configure your `docker-compose` or Expo config to proxy API calls so everything runs on one domain.

### Step 4: Websockets (Important for Realtime)

Supabase Realtime needs Websocket headers.

1. In the Reverse Proxy rule, click **Custom Header**.

2. Create: `Upgrade` -> `$http_upgrade`.

3. Create: `Connection` -> `$connection_upgrade`.

## 8. Storage & Backups (Backblaze B2) ☁️

Since you already use Backblaze on Synology, follow this structure to ensure safe, consistent backups.

### 1. Recommended Folder Structure

Organize your volume mappings to separate "Live Data" from "Safe-to-Backup Data".

```bash



/volume1/docker/kitchen/



├── docker-compose.yml



└── volumes/



    ├── db_raw/       # ⚠️ DO NOT SYNC LIVE. Raw Postgres files.



    ├── storage/      # ✅ SYNC. User uploaded images (Vision).



    └── backups/      # ✅ SYNC. Scheduled SQL dumps.



```

### 2. Configure Docker Compose

Update your `docker-compose.yml` volumes to map to these host paths:

```yaml



services:



  db:



    volumes:



      - ./volumes/db_raw:/var/lib/postgresql/data



  storage:



    volumes:



      - ./volumes/storage:/var/lib/storage



```

### 3. Database Backup Strategy (The "Safe" Way)

Raw database files can be corrupted if synced while the DB is writing. Instead, schedule a nightly dump.

1. Open Synology **Control Panel** > **Task Scheduler**.

2. **Create** > **Scheduled Task** > **User-defined script**.

3. **Task Settings**:

    - User: `root`

    - Schedule: Daily at 3 AM.

    - **Run Command**:

      ```bash



      # Keep last 7 days of backups



      find /volume1/docker/kitchen/volumes/backups -type f -mtime +7 -name '*.sql.gz' -delete



      



      # Dump Database



      docker exec kitchen-db-1 pg_dumpall -c -U postgres | gzip > /volume1/docker/kitchen/volumes/backups/db_$(date +\%F).sql.gz



      ```

### 4. Cloud Sync Configuration

Now configure **Cloud Sync** to target only the safe folders.

1. Open **Cloud Sync**.

2. Add **Backblaze B2** task.

3. **Local Path**: `/volume1/docker/kitchen/volumes/`.

4. **Filter/Subfolders**:

    - ✅ Select `backups/`

    - ✅ Select `storage/`

    - ❌ **Uncheck** `db_raw/` (Crucial!)

This ensures you have a point-in-time recovery for the DB and a live backup of all photos.

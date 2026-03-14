# Running Kitchen Inside a Yolo Jail 🐳🔒

> Everything runs inside the container. No host Docker required.

## TL;DR

```bash
./scripts/jail-stack.sh up      # Start full Supabase stack (podman-in-podman)
./scripts/jail-stack.sh seed    # Seed dev user + household
just dev-api                    # Start Kitchen API on :5300
just dev-frontend               # Start Expo web on :8200
python3 -m pytest tests/ -v    # Run all 409 tests
./scripts/jail-stack.sh down    # Tear it all down
```

## Why This Exists

The yolo jail is already a podman container. Normally the Kitchen stack runs via
`docker compose` on the host, but inside the jail there's no host Docker. This
setup runs the **entire Supabase infrastructure** using nested podman — containers
inside a container — so development is fully self-contained. 🐋

Fun fact: a whale inside a whale is called a "Russian nesting whale." I just made
that up, but it should be a thing. 🪆

## How It Works

### The Pod Architecture

All 8 Supabase services run in a single **podman pod** with `--network=host`:

```
┌─────────────────── yolo jail (outer podman container) ───────────────────┐
│                                                                          │
│  ┌──────────────── kitchen-jail pod (shared network) ─────────────────┐  │
│  │                                                                    │  │
│  │  ┌──────────┐ ┌──────┐ ┌──────┐ ┌──────────┐ ┌──────────┐        │  │
│  │  │PostgreSQL│ │ Kong │ │ Auth │ │PostgREST │ │ Realtime │        │  │
│  │  │  :5432   │ │:8250 │ │:9999 │ │  :3000   │ │  :4000   │        │  │
│  │  └──────────┘ └──────┘ └──────┘ └──────────┘ └──────────┘        │  │
│  │                                                                    │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐                           │  │
│  │  │  Meta    │ │ Storage  │ │  Studio  │                           │  │
│  │  │  :8080   │ │  :5000   │ │  :5303   │                           │  │
│  │  └──────────┘ └──────────┘ └──────────┘                           │  │
│  │                                                                    │  │
│  │  All services talk via localhost (shared network namespace)        │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────── Native processes (no container) ───────────────────┐  │
│  │  Kitchen API (uvicorn :5300)  │  Expo Web (metro :8200)           │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

### Why Pods? Why Host Networking?

**Bridge networking is blocked** inside nested containers — netavark can't create
virtual network interfaces without `CAP_NET_ADMIN`. A podman **pod** solves this
elegantly:

- All containers in a pod share one network namespace (like localhost)
- The pod uses `--network=host` to bind to the jail's network
- Services communicate via `localhost:<port>` — no DNS, no bridge, no hassle

### Key Differences from docker-compose

| Aspect | docker-compose (host) | jail-stack.sh (jail) |
|--------|----------------------|---------------------|
| Runtime | Docker | Podman (nested) |
| Networking | Bridge (`kitchen-network`) | Host via pod |
| Service discovery | Container names (`db`, `kong`) | `localhost` ports |
| Kong config | `kong.yml.template` | `kong-jail.yml` (localhost URLs) |
| PostgreSQL port | 54322 (mapped) | 5432 (default, direct) |
| Studio port | Via `STUDIO_PORT` env | Via `PORT` env (Next.js) |

## Commands Reference

### Stack Management

```bash
# Start everything (pulls images on first run — ~2 min)
./scripts/jail-stack.sh up

# Stop and remove all containers
./scripts/jail-stack.sh down

# Check what's running
./scripts/jail-stack.sh status

# View logs (all services, last 5 lines each)
./scripts/jail-stack.sh logs

# View logs for a specific service
./scripts/jail-stack.sh logs db
./scripts/jail-stack.sh logs auth
./scripts/jail-stack.sh logs kong

# Open a psql shell
./scripts/jail-stack.sh psql

# Seed the dev user and household
./scripts/jail-stack.sh seed
```

### Running the App

After `jail-stack.sh up` and `seed`:

```bash
# Start the Kitchen API (connects to jail-local Supabase)
SUPABASE_URL=http://localhost:8250 just dev-api

# Or manually:
SUPABASE_URL=http://localhost:8250 \
  SUPABASE_SERVICE_ROLE_KEY=<your-key> \
  python3 -B -m uvicorn src.api.main:app --host 0.0.0.0 --port 5300
```

### Running Tests

```bash
# All 409 backend tests
SUPABASE_URL=http://localhost:8250 python3 -m pytest tests/ -v

# With coverage
SUPABASE_URL=http://localhost:8250 python3 -m pytest tests/ --cov=src/api
```

## Services & Ports

| Service | Port | Purpose | Health Check |
|---------|------|---------|-------------|
| PostgreSQL | 5432 | Database | `pg_isready` |
| Kong | 8250 | Supabase API Gateway | `curl :8250/rest/v1/` |
| GoTrue | 9999 | Authentication | `curl :8250/auth/v1/health` |
| PostgREST | 3000 | Auto-REST API | `curl :3000/` |
| Realtime | 4000 | WebSocket subscriptions | Slow startup (~30s) |
| Postgres Meta | 8080 | DB metadata (for Studio) | `curl :8080/` |
| Storage | 5000 | File storage | `curl :5000/` |
| Studio | 5303 | Admin UI | `curl :5303/` |
| Kitchen API | 5300 | FastAPI backend | `curl :5300/health` |
| Expo Web | 8200 | Frontend | `curl :8200/` |

## Troubleshooting 🔧

### "PostgreSQL did not start within 60s"

Check the DB logs — usually a SQL init error:

```bash
podman logs kitchen-jail-db 2>&1 | tail -20
```

Common fix: if the DB volume has stale data from a failed init, prune it:

```bash
./scripts/jail-stack.sh down
podman volume prune -f
./scripts/jail-stack.sh up
```

### "netavark: Netlink error: Operation not permitted"

You tried to run a container without `--network=host` or outside the pod.
Inside a yolo jail, all containers must use host networking or join a pod.

### Studio shows "ENOTFOUND" or "EADDRINUSE"

Studio's Next.js server needs two things:
- `--add-host <pod-name>:127.0.0.1` (resolves the pod hostname)
- `PORT=5303` env (avoids port 3000 conflict with PostgREST)

Both are handled by `jail-stack.sh` automatically.

### Realtime is slow to start

The Realtime service (Erlang/Elixir) takes 30-45 seconds to boot. The script
waits but won't block on it — this is normal and non-fatal.

## What Changed in the DB Init Scripts

Two fixes were needed for the Supabase Postgres 15 image:

1. **`01_schema.sql`**: `CREATE PUBLICATION IF NOT EXISTS` → PG15-compatible
   `DO $$ ... IF NOT EXISTS ... END $$` block.

2. **`04_realtime_tenant.sql`**: The `_realtime.tenants` table doesn't exist at
   DB init time (it's created by the Realtime container on first startup). The
   script now checks `information_schema.tables` before attempting any inserts
   and uses dynamic SQL to avoid parse-time errors.

These fixes also improve the docker-compose path — they were latent bugs. 🐛

## Architecture Notes

- The Kitchen API and Expo frontend run as **native processes** (not containers)
  since all their dependencies are already in the jail's nix environment
- Container images are pulled from Docker Hub on first run and cached in
  `/var/lib/containers/storage/`
- The pod's infra container is lightweight (~1MB) — it just holds the network
  namespace
- Total disk for all images: ~2.5 GB

#!/usr/bin/env bash
# =============================================================================
# jail-stack.sh — Run the full Kitchen Supabase stack inside a yolo jail
#
# Uses podman pods with host networking (bridge networking is blocked inside
# nested containers). All services share a network namespace via the pod,
# so they communicate over localhost.
#
# Usage:
#   ./scripts/jail-stack.sh up        # Start the stack
#   ./scripts/jail-stack.sh down      # Stop and remove everything
#   ./scripts/jail-stack.sh status    # Show running containers
#   ./scripts/jail-stack.sh logs [svc] # Tail logs (all or specific service)
#   ./scripts/jail-stack.sh seed      # Seed dev data
#   ./scripts/jail-stack.sh psql      # Open psql shell
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
INFRA_DIR="$PROJECT_ROOT/infra/docker"
POD_NAME="kitchen-jail"

# Load env
set -a
source "$PROJECT_ROOT/.env"
set +a

# Pod-internal ports (services talk over localhost inside the pod)
# These match the default ports each service expects.
PGPORT=5432
KONG_PORT="${SUPABASE_PORT:-8250}"
STUDIO_INTERNAL_PORT="${STUDIO_PORT:-5303}"

# Kong config with localhost URLs (pod shares network namespace)
KONG_CONFIG_JAIL="$INFRA_DIR/volumes/kong/kong-jail.yml"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
log()  { echo "🐳 $*"; }
err()  { echo "❌ $*" >&2; }
ok()   { echo "✅ $*"; }

wait_for_port() {
  local port=$1 name=$2 max=${3:-30}
  log "Waiting for $name on port $port..."
  for i in $(seq 1 "$max"); do
    if bash -c "echo >/dev/tcp/127.0.0.1/$port" 2>/dev/null; then
      ok "$name is up (port $port)"
      return 0
    fi
    sleep 1
  done
  err "$name did not start within ${max}s on port $port"
  return 1
}

generate_kong_config() {
  # In a pod, all services are on localhost
  cat > "$KONG_CONFIG_JAIL" <<KONG_EOF
_format_version: "2.1"

services:
  - name: auth
    url: http://localhost:9999
    routes:
      - name: auth
        paths:
          - /auth/v1
        strip_path: true

  - name: rest
    url: http://localhost:3000
    routes:
      - name: rest
        paths:
          - /rest/v1
        strip_path: true

  - name: realtime
    url: http://localhost:4000
    routes:
      - name: realtime
        paths:
          - /realtime/v1
        strip_path: true

  - name: storage
    url: http://localhost:5000
    routes:
      - name: storage
        paths:
          - /storage/v1
        strip_path: true

  - name: meta
    url: http://localhost:8080
    routes:
      - name: meta
        paths:
          - /pg
        strip_path: true

plugins:
  - name: cors
    config:
      origins:
        - "*"
      methods:
        - GET
        - POST
        - PUT
        - PATCH
        - DELETE
        - OPTIONS
        - HEAD
      headers:
        - "*"
      exposed_headers:
        - "*"
      credentials: true
      max_age: 3600

consumers:
  - username: anon
    keyauth_credentials:
      - key: ${ANON_KEY}
  - username: service_role
    keyauth_credentials:
      - key: ${SERVICE_ROLE_KEY}
KONG_EOF
  ok "Generated Kong jail config"
}

# ---------------------------------------------------------------------------
# Stack UP
# ---------------------------------------------------------------------------
cmd_up() {
  log "Starting Kitchen stack in jail pod..."

  # Generate localhost Kong config
  generate_kong_config

  # Clean up any existing pod
  podman pod exists "$POD_NAME" 2>/dev/null && {
    log "Removing existing pod..."
    podman pod rm -f "$POD_NAME" 2>/dev/null || true
  }

  # Create pod with host networking (only option in nested containers)
  log "Creating pod '$POD_NAME' with host networking..."
  podman pod create \
    --name "$POD_NAME" \
    --network=host \
    --infra-name="${POD_NAME}-infra"
  ok "Pod created"

  # --- 1. PostgreSQL (port 5432) ---
  log "Starting PostgreSQL..."
  podman run -d \
    --pod "$POD_NAME" \
    --name "${POD_NAME}-db" \
    -e POSTGRES_USER=postgres \
    -e "POSTGRES_PASSWORD=${POSTGRES_PASSWORD}" \
    -e POSTGRES_DB=postgres \
    -v "${INFRA_DIR}/volumes/db/init:/docker-entrypoint-initdb.d:ro" \
    docker.io/supabase/postgres:15.6.1.143

  wait_for_port $PGPORT "PostgreSQL" 60

  # --- 2. Kong API Gateway ---
  log "Starting Kong..."
  podman run -d \
    --pod "$POD_NAME" \
    --name "${POD_NAME}-kong" \
    -e KONG_DATABASE=off \
    -e KONG_DECLARATIVE_CONFIG=/home/kong/kong.yml \
    -e KONG_DNS_ORDER="LAST,A,CNAME" \
    -e KONG_PLUGINS="request-transformer,cors,key-auth,acl,basic-auth" \
    -e KONG_NGINX_PROXY_PROXY_BUFFER_SIZE=160k \
    -e "KONG_NGINX_PROXY_PROXY_BUFFERS=64 160k" \
    -e "KONG_PROXY_LISTEN=0.0.0.0:${KONG_PORT}, 0.0.0.0:8443 ssl" \
    -v "${KONG_CONFIG_JAIL}:/home/kong/kong.yml:ro" \
    docker.io/library/kong:2.8.1

  wait_for_port "$KONG_PORT" "Kong" 30

  # --- 3. GoTrue Auth (port 9999) ---
  log "Starting GoTrue Auth..."
  podman run -d \
    --pod "$POD_NAME" \
    --name "${POD_NAME}-auth" \
    -e GOTRUE_API_HOST=0.0.0.0 \
    -e GOTRUE_API_PORT=9999 \
    -e "API_EXTERNAL_URL=${API_EXTERNAL_URL:-http://localhost:8000}" \
    -e GOTRUE_DB_DRIVER=postgres \
    -e "GOTRUE_DB_DATABASE_URL=postgres://supabase_auth_admin:${POSTGRES_PASSWORD}@localhost:${PGPORT}/postgres" \
    -e "GOTRUE_SITE_URL=${SITE_URL:-http://localhost:3000}" \
    -e "GOTRUE_URI_ALLOW_LIST=${ADDITIONAL_REDIRECT_URLS:-}" \
    -e "GOTRUE_DISABLE_SIGNUP=${DISABLE_SIGNUP:-false}" \
    -e GOTRUE_JWT_ADMIN_ROLES=service_role \
    -e GOTRUE_JWT_AUD=authenticated \
    -e GOTRUE_JWT_DEFAULT_GROUP_NAME=authenticated \
    -e "GOTRUE_JWT_EXP=${JWT_EXPIRY:-3600}" \
    -e "GOTRUE_JWT_SECRET=${JWT_SECRET}" \
    -e "GOTRUE_EXTERNAL_EMAIL_ENABLED=true" \
    -e "GOTRUE_EXTERNAL_ANONYMOUS_USERS_ENABLED=${ENABLE_ANONYMOUS_USERS:-false}" \
    -e "GOTRUE_MAILER_AUTOCONFIRM=${ENABLE_EMAIL_AUTOCONFIRM:-true}" \
    docker.io/supabase/gotrue:v2.164.0

  wait_for_port 9999 "GoTrue Auth" 30

  # --- 4. PostgREST (port 3000) ---
  log "Starting PostgREST..."
  podman run -d \
    --pod "$POD_NAME" \
    --name "${POD_NAME}-rest" \
    -e "PGRST_DB_URI=postgres://authenticator:${POSTGRES_PASSWORD}@localhost:${PGPORT}/postgres" \
    -e PGRST_DB_SCHEMAS=public,storage,graphql_public \
    -e PGRST_DB_ANON_ROLE=anon \
    -e "PGRST_JWT_SECRET=${JWT_SECRET}" \
    -e PGRST_DB_USE_LEGACY_GUCS=false \
    -e "PGRST_APP_SETTINGS_JWT_SECRET=${JWT_SECRET}" \
    -e "PGRST_APP_SETTINGS_JWT_EXP=${JWT_EXPIRY:-3600}" \
    docker.io/postgrest/postgrest:v12.2.0

  wait_for_port 3000 "PostgREST" 30

  # --- 5. Realtime (port 4000) ---
  log "Starting Realtime..."
  podman run -d \
    --pod "$POD_NAME" \
    --name "${POD_NAME}-realtime" \
    -e APP_NAME=realtime \
    -e PORT=4000 \
    -e DB_HOST=localhost \
    -e "DB_PORT=${PGPORT}" \
    -e DB_USER=supabase_admin \
    -e "DB_PASSWORD=${POSTGRES_PASSWORD}" \
    -e DB_NAME=postgres \
    -e "DB_AFTER_CONNECT_QUERY=SET search_path TO _realtime" \
    -e DB_ENC_KEY=supabaserealtime \
    -e "API_JWT_SECRET=${JWT_SECRET}" \
    -e "SECRET_KEY_BASE=${SECRET_KEY_BASE:-UpNVntn3cDxHJpq99YMc1T1AQgQpc8kfYTuRgBiYa15BLrx8etQoXz3gZv1/u2oq}" \
    -e "ERL_AFLAGS=-proto_dist inet_tcp" \
    -e "DNS_NODES=''" \
    -e RLIMIT_NOFILE=10000 \
    -e SEED_SELF_HOST=true \
    docker.io/supabase/realtime:v2.30.34

  # Realtime is slow to start — don't block on it
  wait_for_port 4000 "Realtime" 45 || log "Realtime may still be starting (non-fatal)..."

  # --- 6. Postgres Meta (port 8080) ---
  log "Starting Postgres Meta..."
  podman run -d \
    --pod "$POD_NAME" \
    --name "${POD_NAME}-meta" \
    -e PG_META_PORT=8080 \
    -e PG_META_DB_HOST=localhost \
    -e "PG_META_DB_PORT=${PGPORT}" \
    -e PG_META_DB_NAME=postgres \
    -e PG_META_DB_USER=supabase_admin \
    -e "PG_META_DB_PASSWORD=${POSTGRES_PASSWORD}" \
    docker.io/supabase/postgres-meta:v0.84.2

  wait_for_port 8080 "Postgres Meta" 30

  # --- 7. Storage (port 5000) ---
  log "Starting Storage..."
  podman run -d \
    --pod "$POD_NAME" \
    --name "${POD_NAME}-storage" \
    -e "ANON_KEY=${ANON_KEY}" \
    -e "SERVICE_KEY=${SERVICE_ROLE_KEY}" \
    -e POSTGREST_URL=http://localhost:3000 \
    -e "PGRST_JWT_SECRET=${JWT_SECRET}" \
    -e "DATABASE_URL=postgres://supabase_storage_admin:${POSTGRES_PASSWORD}@localhost:${PGPORT}/postgres" \
    -e FILE_SIZE_LIMIT=52428800 \
    -e STORAGE_BACKEND=file \
    -e FILE_STORAGE_BACKEND_PATH=/var/lib/storage \
    -e TENANT_ID=stub \
    -e REGION=stub \
    -e GLOBAL_S3_BUCKET=stub \
    docker.io/supabase/storage-api:v1.11.13

  wait_for_port 5000 "Storage" 30

  # --- 8. Studio (Next.js on STUDIO_PORT) ---
  # Studio defaults to port 3000 which conflicts with PostgREST.
  # Use PORT env to relocate. --add-host resolves the pod hostname.
  log "Starting Studio..."
  podman run -d \
    --pod "$POD_NAME" \
    --name "${POD_NAME}-studio" \
    --add-host "${POD_NAME}:127.0.0.1" \
    -e HOSTNAME=0.0.0.0 \
    -e "PORT=${STUDIO_INTERNAL_PORT}" \
    -e STUDIO_PG_META_URL=http://localhost:8080 \
    -e "POSTGRES_PASSWORD=${POSTGRES_PASSWORD}" \
    -e DEFAULT_ORGANIZATION_NAME=Kitchen \
    -e DEFAULT_PROJECT_NAME=Kitchen \
    -e "SUPABASE_URL=http://localhost:${KONG_PORT}" \
    -e "SUPABASE_PUBLIC_URL=${API_EXTERNAL_URL:-http://localhost:${KONG_PORT}}" \
    -e "SUPABASE_ANON_KEY=${ANON_KEY}" \
    -e "SUPABASE_SERVICE_KEY=${SERVICE_ROLE_KEY}" \
    docker.io/supabase/studio:20241202-71e5240

  wait_for_port "$STUDIO_INTERNAL_PORT" "Studio" 30

  echo ""
  ok "Kitchen stack is up! 🎉"
  echo ""
  echo "  📊 Supabase Studio: http://localhost:${STUDIO_INTERNAL_PORT}"
  echo "  🔌 Supabase API:    http://localhost:${KONG_PORT}"
  echo "  🐘 PostgreSQL:      localhost:${PGPORT}"
  echo ""
  echo "  Next steps:"
  echo "    ./scripts/jail-stack.sh seed     # Seed dev data"
  echo "    just dev-api                     # Start Kitchen API"
  echo "    just dev-frontend                # Start Expo web"
  echo ""
}

# ---------------------------------------------------------------------------
# Stack DOWN
# ---------------------------------------------------------------------------
cmd_down() {
  log "Stopping Kitchen stack..."
  if podman pod exists "$POD_NAME" 2>/dev/null; then
    podman pod stop "$POD_NAME" -t 10 2>/dev/null || true
    podman pod rm -f "$POD_NAME" 2>/dev/null || true
    ok "Pod '$POD_NAME' removed"
  else
    log "Pod '$POD_NAME' not found — nothing to do"
  fi
}

# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------
cmd_status() {
  if ! podman pod exists "$POD_NAME" 2>/dev/null; then
    echo "Pod '$POD_NAME' does not exist."
    return 1
  fi
  podman pod ps --filter "name=$POD_NAME"
  echo ""
  podman ps --pod --filter "pod=$POD_NAME" --format \
    "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

# ---------------------------------------------------------------------------
# Logs
# ---------------------------------------------------------------------------
cmd_logs() {
  local svc="${1:-}"
  if [ -n "$svc" ]; then
    podman logs -f "${POD_NAME}-${svc}" 2>&1
  else
    # Tail all containers in the pod
    for ctr in $(podman ps --pod --filter "pod=$POD_NAME" --format "{{.Names}}" | rg -v infra); do
      echo "=== $ctr ==="
      podman logs --tail 5 "$ctr" 2>&1
      echo ""
    done
  fi
}

# ---------------------------------------------------------------------------
# Seed
# ---------------------------------------------------------------------------
cmd_seed() {
  log "Seeding dev data..."
  cd "$PROJECT_ROOT"
  SUPABASE_URL="http://localhost:${SUPABASE_PORT}" \
    uv run python scripts/seed_dev_data.py
}

# ---------------------------------------------------------------------------
# PSQL shell
# ---------------------------------------------------------------------------
cmd_psql() {
  podman exec -it "${POD_NAME}-db" psql -U postgres -p "${PGPORT}"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
case "${1:-help}" in
  up)     cmd_up ;;
  down)   cmd_down ;;
  status) cmd_status ;;
  logs)   cmd_logs "${2:-}" ;;
  seed)   cmd_seed ;;
  psql)   cmd_psql ;;
  *)
    echo "Usage: $0 {up|down|status|logs [service]|seed|psql}"
    echo ""
    echo "Services: db, kong, auth, rest, realtime, meta, storage, studio"
    exit 1
    ;;
esac

-- ==========================================================================
-- Realtime Tenant Configuration 📡
-- 
-- Creates a tenant alias for WebSocket subscriptions to work.
-- The SEED_SELF_HOST=true creates 'realtime-dev', but Kong routes as 'realtime'.
-- This script creates an alias so both work.
--
-- Note: The _realtime.tenants table is created by the realtime container on
-- first startup, not during DB init. This script skips gracefully when the
-- table doesn't exist yet — the realtime container handles it.
--
-- Fun fact: Supabase Realtime can handle millions of concurrent connections! 🚀
-- ==========================================================================

DO $$
BEGIN
    -- Only run if the _realtime.tenants table exists (created by realtime container)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = '_realtime' AND table_name = 'tenants'
    ) THEN
        RAISE NOTICE 'Skipping realtime tenant setup — _realtime.tenants not yet created';
        RETURN;
    END IF;

    -- Use dynamic SQL to avoid parse-time errors
    EXECUTE '
        INSERT INTO _realtime.tenants (
            id, name, external_id, jwt_secret, max_bytes_per_second,
            max_channels_per_client, max_concurrent_users, max_events_per_second,
            max_joins_per_second, notify_private_alpha, suspend, inserted_at, updated_at
        )
        SELECT 
            gen_random_uuid(), ''realtime'', ''realtime'', jwt_secret, max_bytes_per_second,
            max_channels_per_client, max_concurrent_users, max_events_per_second,
            max_joins_per_second, notify_private_alpha, suspend, now(), now()
        FROM _realtime.tenants
        WHERE external_id = ''realtime-dev''
          AND NOT EXISTS (SELECT 1 FROM _realtime.tenants WHERE external_id = ''realtime'')
    ';

    EXECUTE '
        INSERT INTO _realtime.extensions (
            id, type, settings, tenant_external_id, inserted_at, updated_at
        )
        SELECT 
            gen_random_uuid(), type, settings, ''realtime'', now(), now()
        FROM _realtime.extensions
        WHERE tenant_external_id = ''realtime-dev''
          AND NOT EXISTS (SELECT 1 FROM _realtime.extensions WHERE tenant_external_id = ''realtime'')
    ';

    RAISE NOTICE 'Created realtime tenant alias';
END $$;

-- ==========================================================================
-- Realtime Tenant Configuration 📡
-- 
-- Creates a tenant alias for WebSocket subscriptions to work.
-- The SEED_SELF_HOST=true creates 'realtime-dev', but Kong routes as 'realtime'.
-- This script creates an alias so both work.
--
-- Fun fact: Supabase Realtime can handle millions of concurrent connections! 🚀
-- ==========================================================================

-- Wait for realtime to seed first, then create the alias tenant
-- This runs AFTER the realtime container seeds on startup
DO $$
BEGIN
    -- Only create if realtime-dev exists but realtime doesn't
    IF EXISTS (SELECT 1 FROM _realtime.tenants WHERE external_id = 'realtime-dev')
       AND NOT EXISTS (SELECT 1 FROM _realtime.tenants WHERE external_id = 'realtime')
    THEN
        -- Copy the realtime-dev tenant to create a 'realtime' tenant
        INSERT INTO _realtime.tenants (
            id, name, external_id, jwt_secret, max_bytes_per_second,
            max_channels_per_client, max_concurrent_users, max_events_per_second,
            max_joins_per_second, notify_private_alpha, suspend, inserted_at, updated_at
        )
        SELECT 
            gen_random_uuid(), 'realtime', 'realtime', jwt_secret, max_bytes_per_second,
            max_channels_per_client, max_concurrent_users, max_events_per_second,
            max_joins_per_second, notify_private_alpha, suspend, now(), now()
        FROM _realtime.tenants
        WHERE external_id = 'realtime-dev';

        -- Copy the extension configuration
        INSERT INTO _realtime.extensions (
            id, type, settings, tenant_external_id, inserted_at, updated_at
        )
        SELECT 
            gen_random_uuid(), type, settings, 'realtime', now(), now()
        FROM _realtime.extensions
        WHERE tenant_external_id = 'realtime-dev';
        
        RAISE NOTICE 'Created realtime tenant alias';
    END IF;
END $$;

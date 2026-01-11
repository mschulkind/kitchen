# Data Loading & Management 📊

This guide covers how to populate your Kitchen with data, migrate from Phase 0, and manage backups.

## 1. Initial Seeding

When you first start the stack, the database is empty. You have two options:

### Option A: Clean Slate (Recommended)

Just start using the app. Add items to your pantry manually via the "Inventory" tab.

### Option B: Bulk Seed Script

We provide a script to seed common staples.

```bash
# From local machine
cd src/api
uv run python scripts/seed_staples.py --household-id "YOUR_ID"
```

*This adds salt, oil, flour, sugar, etc., with default quantities.*

## 2. Importing "Winner" Recipes (Phase 0)

If you have Markdown recipes in `phase0_flow/recipes/` that you want to keep:

1. **Prepare the Files**: Ensure they have frontmatter metadata if possible (Title, Source).
2. **Run the Importer**:

    ```bash
    uv run python scripts/import_legacy_recipes.py \
        --input-dir "../../phase0_flow/plans/2026-01-10_chili-and-dads/recipes" \
        --household-id "YOUR_ID"
    ```

3. **Verify**: Check the App's Recipe tab. The importer attempts to parse ingredients using the Phase 2B Parser.

## 3. Backups

### Database (Postgres)

Since you are hosting on Synology, use **Hyper Backup** to back up the `/docker/kitchen/infra/docker/volumes/db` folder. This is the simplest robust method.

**Manual Dump**:

```bash
docker exec -t kitchen-db-1 pg_dumpall -c -U postgres > dump_$(date +%F).sql
```

### Images (Supabase Storage)

Back up the `storage` volume if you are using local filesystem storage for pantry photos.

## 4. Resetting Data

**⚠️ Danger Zone**: To wipe everything and start over.

```bash
docker compose down -v
# The -v flag removes the named volumes
docker compose up -d
```

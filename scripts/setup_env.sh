#!/bin/bash
set -e

# Copy .env if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

# Check if keys are actually set (not placeholders)
if grep -q "your-service-role-key" .env || ! grep -q "SERVICE_ROLE_KEY" .env; then
    echo "Generating Supabase keys..."
    # Generate keys
    KEYS=$(uv run scripts/generate_supabase_keys.py)
    
    # Remove old placeholders/keys if they exist
    sed -i '/JWT_SECRET=/d' .env
    sed -i '/ANON_KEY=/d' .env
    sed -i '/SERVICE_ROLE_KEY=/d' .env
    
    # Append new keys
    echo "" >> .env
    echo "$KEYS" >> .env
fi

echo "Environment variables set up."
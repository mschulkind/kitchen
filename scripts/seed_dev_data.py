#!/usr/bin/env python3
import os
import sys
import time
import httpx
from dotenv import load_dotenv

def seed_data():
    load_dotenv()
    
    port = os.getenv("SUPABASE_PORT", "8250")
    url = os.getenv("SUPABASE_URL", f"http://localhost:{port}")
    key = os.getenv("SERVICE_ROLE_KEY")
    
    if not key:
        print("Error: SERVICE_ROLE_KEY not found in .env")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {key}",
        "apikey": key,
        "Content-Type": "application/json"
    }

    email = "admin@kitchen.local"
    password = "admin123"
    user_id = "d0000000-0000-0000-0000-000000000001"

    print(f"Ensuring dev user {email} exists at {url}...")

    with httpx.Client() as client:
        # 1. Create User in Auth (if not exists)
        auth_url = f"{url}/auth/v1/admin/users"
        user_data = {
            "id": user_id,
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {"display_name": "Dev Admin"}
        }
        
        try:
            response = client.post(auth_url, headers=headers, json=user_data)
            
            if response.status_code == 201:
                print(f"✅ User {email} created successfully.")
            elif response.status_code == 422:
                print(f"ℹ️ User {email} already exists.")
            elif response.status_code == 404:
                print(f"❌ Auth service not found at {auth_url}. Check if Docker is up.")
                return False
            else:
                print(f"❌ Auth error: {response.status_code} {response.text}")
                return False

            # 2. Ensure user is in public.users
            public_users_url = f"{url}/rest/v1/users"
            client.post(public_users_url, headers=headers, json={
                "id": user_id,
                "email": email,
                "display_name": "Dev Admin"
            })

            # 3. Create a default household
            print("Ensuring default household exists...")
            household_id = "h0000000-0000-0000-0000-000000000001"
            
            households_url = f"{url}/rest/v1/households"
            client.post(households_url, headers=headers, json={
                "id": household_id,
                "name": "Dev Kitchen",
                "owner_id": user_id
            })

            # 4. Link user to household
            members_url = f"{url}/rest/v1/household_members"
            client.post(members_url, headers=headers, json={
                "household_id": household_id,
                "user_id": user_id,
                "role": "owner"
            })

            print("🚀 Dev setup complete! You can now log in at /devlogin")
            return True
            
        except httpx.ConnectError:
            print(f"⏳ Connection to {url} failed. Is Docker running?")
            return False

if __name__ == "__main__":
    # Wait for service to be ready
    max_retries = 15
    for i in range(max_retries):
        if seed_data():
            break
        print(f"Retrying... ({i+1}/{max_retries})")
        time.sleep(5)
    else:
        print("❌ Could not connect to Supabase after multiple attempts.")
        sys.exit(1)
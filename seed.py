import json
import os
from supabase import create_client, Client
from uuid6 import uuid7
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Safety check
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase credentials in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def seed_database(file_path: str):
    print(f"Reading data from {file_path}...")
    
    # 1. Open and load the JSON file
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # 2. Extract the list from the "profiles" key!
    profiles = data.get("profiles", [])
    
    if not profiles:
        print("No profiles found in the file. Check the JSON structure.")
        return

    print(f"Found {len(profiles)} profiles. Preparing for database upload...")

    # 3. Format with UUIDv7
    formatted_profiles = []
    for p in profiles:
        formatted_profiles.append({
            "id": str(uuid7()), # Generating a true UUID v7
            "name": p["name"],
            "gender": p["gender"],
            "gender_probability": p["gender_probability"],
            "age": p["age"],
            "age_group": p["age_group"],
            "country_id": p["country_id"],
            "country_name": p["country_name"],
            "country_probability": p["country_probability"]
        })

    # 4. Upsert in batches of 500 to prevent payload too large errors
    batch_size = 500
    for i in range(0, len(formatted_profiles), batch_size):
        batch = formatted_profiles[i:i+batch_size]
        # upsert based on the unique 'name' field
        response = supabase.table("profiles").upsert(batch, on_conflict="name").execute()
        print(f"Upserted batch {i // batch_size + 1}...")

    print(f"Seeding completely finished! All {len(formatted_profiles)} profiles are in Supabase.")

if __name__ == "__main__":
    # Updated to match the exact name of the file you uploaded
    seed_database("seed_profiles.json")
from supabase_client import supabase
from datetime import datetime, timedelta, timezone

# Insert new data
data = {
    "linkedin_id": "BiXLFEGlD6",
    "email": "2021ee313@student.uet.edu.pk",
    "access_token": "AQWqCme3xzzG_frF...",  # your LinkedIn token
    "expires_at": (datetime.now(timezone.utc) + timedelta(days=60)).isoformat()  # UTC + 60 days
}

# Insert into Supabase table
insert_res = supabase.table("linkedin_tokens").insert(data).execute()
print("✅ Insert result:", insert_res)

# Fetch all rows to check changes
fetch_res = supabase.table("linkedin_tokens").select("*").execute()
print("\n📋 Current Table Data:")
for row in fetch_res.data:
    print(row)

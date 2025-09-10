from __future__ import annotations
import json, os, requests
from werkzeug.utils import secure_filename

APP_FILE = "sites.json"

# -----------------------
# Simple local persistence
# -----------------------
def load_sites():
    if not os.path.exists(APP_FILE):
        return []
    with open(APP_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_sites(sites):
    with open(APP_FILE, "w", encoding="utf-8") as f:
        json.dump(sites, f, indent=2)

def next_id(sites):
    if not sites:
        return 1
    return max(s["id"] for s in sites) + 1

def get_site(sites, site_id):
    for s in sites:
        if s["id"] == site_id:
            return s
    return None

def rest_base(base_url: str) -> str:
    return base_url.rstrip("/") + "/wp-json/"

# -----------------------
# Site Registration & Test
# -----------------------
def register_site(name: str, base_url: str, username: str, app_password: str):
    sites = load_sites()
    new = {
        "id": next_id(sites),
        "name": name.strip(),
        "base_url": base_url.rstrip("/"),
        "username": username.strip(),
        "app_password": app_password.strip(),
    }
    sites.append(new)
    save_sites(sites)
    print(f"✅ Site registered successfully! (ID: {new['id']})")
    return new

def test_site(site_id: int):
    sites = load_sites()
    site = get_site(sites, site_id)
    if not site:
        return {"error": "site not found"}

    url = rest_base(site["base_url"]) + "wp/v2/users/me?context=edit"
    resp = requests.get(url, auth=(site["username"], site["app_password"]), timeout=30)
    if resp.status_code == 200:
        print("✅ Auth success:", resp.json()["name"])
        return {"ok": True, "user": resp.json()}
    else:
        print("❌ Auth failed:", resp.text)
        return {"ok": False, "status_code": resp.status_code, "text": resp.text}

if __name__ == "__main__":
    # Example usage (replace with real creds)
    site = register_site(
        name="Cammi Kavtech",
        base_url="https://blogpepper.com/wordpress",
        username="admin",
        app_password="8x8t Vxvm yT5S 2gw0 EUWq iWPv"
    )
    test_site(site["id"])

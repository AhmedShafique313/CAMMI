from __future__ import annotations
import json, os, mimetypes, requests
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from urllib.parse import urlparse
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, render_template_string

# configurations
APP_FILE = "sites.json"
app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

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


# -----------------------
# Helpers for WP calls
# -----------------------
def rest_base(base_url: str) -> str:
    return base_url.rstrip("/") + "/wp-json/"


def guess_mime(filename: str) -> str:
    mime, _ = mimetypes.guess_type(filename)
    return mime or "application/octet-stream"


def upload_media(site: dict, image_bytes: bytes, filename: str) -> dict:
    """Upload bytes to /wp/v2/media. Returns WP media JSON."""
    base = rest_base(site["base_url"])
    url = base + "wp/v2/media"
    headers = {
        "Content-Disposition": f'attachment; filename="{secure_filename(filename)}"',
        "Content-Type": guess_mime(filename),
    }
    resp = requests.post(
        url,
        headers=headers,
        data=image_bytes,
        auth=(site["username"], site["app_password"]),
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def create_post(
    site: dict,
    title: str,
    content: str | None,
    featured_media: int | None,
    publish_at_utc: datetime | None,
) -> dict:
    base = rest_base(site["base_url"])
    url = base + "wp/v2/posts"
    payload = {"title": title, "status": "publish"}
    if content:
        payload["content"] = content
    if featured_media:
        payload["featured_media"] = int(featured_media)

    now_utc = datetime.now(timezone.utc)
    if publish_at_utc and publish_at_utc > now_utc:
        payload["status"] = "future"
        # API expects date_gmt in YYYY-MM-DDTHH:MM:SS (no offset)
        payload["date_gmt"] = publish_at_utc.astimezone(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S"
        )

    resp = requests.post(
        url,
        json=payload,
        auth=(site["username"], site["app_password"]),
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


# -----------------------
# Routes
# -----------------------
@app.get("/health")
def health():
    return {"ok": True}


@app.get("/sites")
def list_sites():
    sites = load_sites()
    # do not return app_password raw
    out = []
    for s in sites:
        clone = s.copy()
        clone.pop("app_password", None)
        out.append(clone)
    return jsonify(out)


# HTML form for site registration
@app.get("/register-site")
def register_site_form():
    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Register WordPress Site</title>
        </head>
        <body>
            <h2>Register Your WordPress Site</h2>
            <form method="post" action="/sites">
                <label>Site Name: <input type="text" name="name" required></label><br><br>
                <label>Base URL: <input type="url" name="base_url" placeholder="https://yoursite.com" required></label><br><br>
                <label>Username: <input type="text" name="username" required></label><br><br>
                <label>App Password: <input type="password" name="app_password" required></label><br><br>
                <button type="submit">Register Site</button>
            </form>
        </body>
        </html>
        """
    )


@app.post("/sites")
def add_site():
    # accept JSON or form data
    if request.is_json:
        data = request.get_json(force=True)
    else:
        data = request.form.to_dict()

    for k in ("name", "base_url", "username", "app_password"):
        if not data.get(k):
            return {"error": f"Missing field {k}"}, 400

    sites = load_sites()
    new = {
        "id": next_id(sites),
        "name": data["name"].strip(),
        "base_url": data["base_url"].rstrip("/"),
        "username": data["username"].strip(),
        "app_password": data["app_password"].strip(),
    }
    sites.append(new)
    save_sites(sites)

    if request.is_json:
        return {"id": new["id"]}, 201
    else:
        return f"<h3>Site registered successfully! (ID: {new['id']})</h3>", 201


@app.post("/sites/<int:site_id>/test")
def test_site(site_id: int):
    sites = load_sites()
    site = get_site(sites, site_id)
    if not site:
        return {"error": "site not found"}, 404
    url = rest_base(site["base_url"]) + "wp/v2/users/me?context=edit"
    resp = requests.get(
        url, auth=(site["username"], site["app_password"]), timeout=30
    )
    if resp.status_code == 200:
        return {"ok": True, "user": resp.json()}
    return {
        "ok": False,
        "status_code": resp.status_code,
        "text": resp.text,
    }, 400


@app.post("/posts/schedule")
def schedule_post():
    data = request.get_json(force=True)
    if not data.get("site_id") or not data.get("title"):
        return {"error": "site_id & title required"}, 400

    sites = load_sites()
    site = get_site(sites, int(data["site_id"]))
    if not site:
        return {"error": "site not found"}, 404

    title = data["title"]
    content_html = data.get("content_html", "")
    image_url = data.get("image_url")
    embed = bool(data.get("embed_image_in_content", False))

    publish_at = data.get("publish_at")  # ISO string
    tz_name = data.get("timezone") or "UTC"
    publish_at_utc = None
    if publish_at:
        try:
            local_zone = ZoneInfo(tz_name)
            dt = datetime.fromisoformat(publish_at)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=local_zone)
            else:
                dt = dt.astimezone(local_zone)
            publish_at_utc = dt.astimezone(timezone.utc)
        except Exception as e:
            return {"error": f"bad publish_at/timezone: {e}"}, 400

    featured_media_id = None
    media_src_url = None
    if image_url:
        try:
            r = requests.get(image_url, timeout=60)
            r.raise_for_status()
            filename = os.path.basename(urlparse(image_url).path) or "image"
            media = upload_media(site, r.content, filename)
            featured_media_id = media.get("id")
            media_src_url = media.get("source_url")
        except Exception as e:
            return {"error": f"image upload failed: {e}"}, 400

    final_content = content_html or ""
    if embed and media_src_url:
        final_content = (
            f'<figure><img src="{media_src_url}" alt="" /></figure>\n' + final_content
        )

    try:
        wp_post = create_post(site, title, final_content, featured_media_id, publish_at_utc)
        return {
            "ok": True,
            "wp_id": wp_post.get("id"),
            "status": wp_post.get("status"),
            "link": wp_post.get("link"),
            "date_gmt": wp_post.get("date_gmt"),
        }, 201
    except Exception as e:
        return {"error": str(e)}, 400


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

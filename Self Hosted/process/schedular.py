from __future__ import annotations
import json, os, mimetypes, requests
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from urllib.parse import urlparse
from werkzeug.utils import secure_filename
from register import load_sites, get_site, rest_base

# -----------------------
# Helpers for WP calls
# -----------------------
def guess_mime(filename: str) -> str:
    mime, _ = mimetypes.guess_type(filename)
    return mime or "application/octet-stream"

def upload_media(site: dict, image_bytes: bytes, filename: str) -> dict:
    base = rest_base(site["base_url"])
    url = base + "wp/v2/media"

    files = {
        "file": (secure_filename(filename), image_bytes, guess_mime(filename)),
    }
    headers = {
        "Content-Disposition": f'attachment; filename="{secure_filename(filename)}"',
    }

    resp = requests.post(
        url,
        headers=headers,
        files=files,
        auth=(site["username"], site["app_password"]),
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()

def create_post(site: dict, title: str, content: str | None,
                featured_media: int | None, publish_at_utc: datetime | None) -> dict:
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
# Main scheduling logic
# -----------------------
def schedule_post(site_id: int, title: str, content_html: str = "",
                  image_path: str = None, embed: bool = False,
                  publish_at: str = None, timezone_name: str = "UTC"):
    sites = load_sites()
    site = get_site(sites, site_id)
    if not site:
        return {"error": "site not found"}

    publish_at_utc = None
    if publish_at:
        try:
            local_zone = ZoneInfo(timezone_name)
            dt = datetime.fromisoformat(publish_at)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=local_zone)
            else:
                dt = dt.astimezone(local_zone)
            publish_at_utc = dt.astimezone(timezone.utc)
        except Exception as e:
            return {"error": f"bad publish_at/timezone: {e}"}

    featured_media_id = None
    media_src_url = None
    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as f:
            media = upload_media(site, f.read(), os.path.basename(image_path))
            featured_media_id = media.get("id")
            media_src_url = media.get("source_url")

    final_content = content_html
    if embed and media_src_url:
        final_content = f'<figure><img src="{media_src_url}" alt="" /></figure>\n' + final_content

    try:
        wp_post = create_post(site, title, final_content, featured_media_id, publish_at_utc)
        print("✅ Post created:", wp_post.get("link"))
        return {
            "ok": True,
            "wp_id": wp_post.get("id"),
            "status": wp_post.get("status"),
            "link": wp_post.get("link"),
            "date_gmt": wp_post.get("date_gmt"),
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Example usage: immediate post
    schedule_post(
        site_id=1,  # change to your registered site ID
        title="Hello from Scheduler",
        content_html="<p>This post was created via schedular.py</p>",
        image_path=None,
        embed=False,
        publish_at=None,  # or "2025-09-10T15:00:00"
        timezone_name="Asia/Karachi"
    )

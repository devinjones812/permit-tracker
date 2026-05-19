"""Push notifications via ntfy.sh."""

import os
import requests

NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "dj-permit-watch-2026")
NTFY_TOKEN = os.environ.get("NTFY_TOKEN", "")


def send(title: str, body: str, url: str = None, priority: str = "urgent"):
    """Send a push notification via ntfy.sh."""
    headers = {"Priority": priority, "Tags": "camping"}
    headers["Title"] = title.encode("utf-8")
    if NTFY_TOKEN:
        headers["Authorization"] = f"Bearer {NTFY_TOKEN}"
    if url:
        headers["Click"] = url
        headers["Actions"] = f"view, Book Now, {url}"

    try:
        resp = requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=body.encode("utf-8"),
            headers=headers,
        )
        if resp.ok:
            print(f"  [✓] Notification sent")
        else:
            print(f"  [!] Notification failed: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"  [!] Notification error: {e}")

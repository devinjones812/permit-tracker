#!/usr/bin/env python3
"""Poll recreation.gov every minute and send a push notification when permits open up."""

import os
import time
import sys
from datetime import datetime
import requests as http_requests
from permit_api import check_permit, BOOKING_URL

# ─── Configuration ───────────────────────────────────────────────────────────

TARGET_DIVISION = os.environ["TARGET_DIVISION"]
TARGET_DATE = os.environ["TARGET_DATE"]
GROUP_SIZE = int(os.environ["GROUP_SIZE"])
POLL_INTERVAL_SECONDS = int(os.environ.get("POLL_INTERVAL_SECONDS", "60"))

# ntfy.sh topic — set this to any unique string (acts as your private channel)
# Install the ntfy app on your phone and subscribe to this same topic
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "permit-tracker-alerts")

# ─── Notification ────────────────────────────────────────────────────────────


def send_notification(title: str, body: str, url: str = None):
    """Send push notification via ntfy.sh (free, no account needed)."""
    headers = {"Priority": "urgent", "Tags": "camping"}
    headers["Title"] = title.encode("utf-8")
    if url:
        headers["Click"] = url
        headers["Actions"] = f"view, Book Now, {url}"

    try:
        resp = http_requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=body.encode("utf-8"),
            headers=headers,
        )
        if resp.ok:
            print(f"  [✓] Push notification sent to topic '{NTFY_TOPIC}'")
        else:
            print(f"  [!] Notification failed: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"  [!] Notification error: {e}")


# ─── Main loop ───────────────────────────────────────────────────────────────


def run():
    print(f"\n{'='*60}")
    print(f"  Permit Monitor")
    print(f"{'='*60}")
    print(f"  Watching:   {TARGET_DIVISION} on {TARGET_DATE}")
    print(f"  Group size: {GROUP_SIZE}")
    print(f"  Interval:   every {POLL_INTERVAL_SECONDS}s")
    print(f"  Notify via: ntfy.sh/{NTFY_TOPIC}")
    print(f"{'='*60}\n")

    already_notified = False

    while True:
        now = datetime.now().strftime("%H:%M:%S")
        try:
            result = check_permit(TARGET_DATE, TARGET_DIVISION, GROUP_SIZE)
        except Exception as e:
            print(f"  [{now}] Error: {e}")
            time.sleep(POLL_INTERVAL_SECONDS)
            continue

        remaining = result["remaining"]
        available = result["available"]

        if available:
            print(f"  [{now}] 🎉 AVAILABLE! {remaining} spots — sending notification...")
            if not already_notified:
                send_notification(
                    title="🎉 Yosemite Permit OPEN!",
                    body=(
                        f"{result['division_name']} on {TARGET_DATE}\n"
                        f"{remaining} spot(s) available (need {GROUP_SIZE})\n"
                        f"Book NOW!"
                    ),
                    url=BOOKING_URL,
                )
                already_notified = True
            else:
                print(f"  [{now}] (already notified, skipping duplicate)")
        elif remaining > 0:
            print(f"  [{now}] ⚠️  {remaining} spots (need {GROUP_SIZE}) — not enough")
            already_notified = False
        else:
            print(f"  [{now}] ❌ 0 spots")
            already_notified = False

        time.sleep(POLL_INTERVAL_SECONDS)


def test():
    """Send a fake alert to verify notifications are working."""
    print(f"\n  Sending test notification to ntfy.sh/{NTFY_TOPIC}...")
    send_notification(
        title="🧪 TEST — Permit Alert Working!",
        body=(
            f"If you see this, your pipeline is working.\n"
            f"You'll be notified when {TARGET_DIVISION} opens on {TARGET_DATE}."
        ),
        url=BOOKING_URL,
    )


if __name__ == "__main__":
    try:
        if "--test" in sys.argv:
            test()
        else:
            run()
    except KeyboardInterrupt:
        print("\n  Stopped.")
        sys.exit(0)

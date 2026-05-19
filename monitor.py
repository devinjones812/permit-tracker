#!/usr/bin/env python3
"""Poll recreation.gov for multiple permits and notify on availability."""

import time
import sys
from datetime import datetime
from permit_api import check_permit
from watches import WATCHES
import notify

POLL_INTERVAL_SECONDS = 60
HEARTBEAT_INTERVAL = 12 * 60 * 60  # 12 hours


def startup_check():
    """Run initial check and send deploy notification."""
    lines = []
    for w in WATCHES:
        try:
            result = check_permit(w["permit_id"], w["date"], w["division_id"], w["group_size"])
            lines.append(f"• {w['name']} ({w['date']}): {result['remaining']} spots, need {w['group_size']}")
        except Exception as e:
            lines.append(f"• {w['name']}: error ({e})")

    notify.send(
        title="Monitor deployed",
        body=f"Watching {len(WATCHES)} permit(s):\n" + "\n".join(lines),
        priority="default",
    )


def run():
    print(f"\n{'='*60}")
    print(f"  Permit Monitor — {len(WATCHES)} watch(es)")
    print(f"{'='*60}")
    for w in WATCHES:
        print(f"  • {w['name']} | {w['date']} | need {w['group_size']}")
    print(f"  Interval: every {POLL_INTERVAL_SECONDS}s")
    print(f"  Notify:   ntfy.sh/{notify.NTFY_TOPIC}")
    print(f"{'='*60}\n")

    startup_check()

    notified = set()
    start_time = time.time()
    last_heartbeat = start_time

    while True:
        now = datetime.now().strftime("%H:%M:%S")

        # Heartbeat
        elapsed = time.time() - start_time
        if time.time() - last_heartbeat >= HEARTBEAT_INTERVAL:
            hours = int(elapsed // 3600)
            summary = ", ".join(w["name"] for w in WATCHES)
            notify.send(
                title="Monitor still running",
                body=f"Running for {hours}h. Watching: {summary}",
                priority="low",
            )
            last_heartbeat = time.time()

        # Check each watch
        for w in WATCHES:
            key = f"{w['permit_id']}:{w['division_id']}:{w['date']}"
            try:
                result = check_permit(w["permit_id"], w["date"], w["division_id"], w["group_size"])
            except Exception as e:
                print(f"  [{now}] {w['name']}: error — {e}")
                continue

            remaining = result["remaining"]

            if result["available"]:
                if key not in notified:
                    print(f"  [{now}] {w['name']}: 🎉 {remaining} spots!")
                    notify.send(
                        title=f"🎉 {w['name']} — OPEN!",
                        body=f"{remaining} spot(s) available on {w['date']} (need {w['group_size']})\nBook NOW!",
                        url=result["booking_url"],
                    )
                    notified.add(key)
                else:
                    print(f"  [{now}] {w['name']}: still available ({remaining}), already notified")
            else:
                if key in notified:
                    notified.discard(key)
                if remaining > 0:
                    print(f"  [{now}] {w['name']}: {remaining} spots (need {w['group_size']})")
                else:
                    print(f"  [{now}] {w['name']}: ❌ 0")

        time.sleep(POLL_INTERVAL_SECONDS)


def test():
    """Send a test notification."""
    print(f"  Sending test notification...")
    notify.send(
        title="🧪 TEST — Permit Monitor",
        body=f"Watching {len(WATCHES)} permit(s). Notifications work!",
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

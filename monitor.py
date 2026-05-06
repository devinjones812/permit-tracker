#!/usr/bin/env python3
"""Poll recreation.gov every minute and send an SMS when permits open up."""

import os
import time
import sys
from datetime import datetime
from twilio.rest import Client as TwilioClient
from permit_api import check_permit, BOOKING_URL

# ─── Configuration ───────────────────────────────────────────────────────────

TARGET_DIVISION = "44585917"
TARGET_DATE = "2026-05-09"
GROUP_SIZE = 3
POLL_INTERVAL_SECONDS = 60

# Twilio credentials (set these as environment variables)
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.environ.get("TWILIO_FROM_NUMBER")  # your Twilio phone number
NOTIFY_TO_NUMBER = os.environ.get("NOTIFY_TO_NUMBER")  # your personal phone number

# ─── SMS ─────────────────────────────────────────────────────────────────────


def send_sms(body: str):
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER, NOTIFY_TO_NUMBER]):
        print(f"  [!] SMS skipped — Twilio env vars not set.")
        print(f"      Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER, NOTIFY_TO_NUMBER")
        return

    client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=body,
        from_=TWILIO_FROM_NUMBER,
        to=NOTIFY_TO_NUMBER,
    )
    print(f"  [✓] SMS sent (sid: {message.sid})")


# ─── Main loop ───────────────────────────────────────────────────────────────


def run():
    print(f"\n{'='*60}")
    print(f"  Permit Monitor")
    print(f"{'='*60}")
    print(f"  Watching:   {TARGET_DIVISION} on {TARGET_DATE}")
    print(f"  Group size: {GROUP_SIZE}")
    print(f"  Interval:   every {POLL_INTERVAL_SECONDS}s")
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
            print(f"  [{now}] 🎉 AVAILABLE! {remaining} spots — sending SMS...")
            if not already_notified:
                send_sms(
                    f"🎉 Yosemite permit OPEN!\n"
                    f"{result['division_name']} on {TARGET_DATE}\n"
                    f"{remaining} spot(s) available (need {GROUP_SIZE})\n"
                    f"Book NOW: {BOOKING_URL}"
                )
                already_notified = True
            else:
                print(f"  [{now}] (already notified, skipping duplicate SMS)")
        elif remaining > 0:
            print(f"  [{now}] ⚠️  {remaining} spots (need {GROUP_SIZE}) — not enough")
            already_notified = False
        else:
            print(f"  [{now}] ❌ 0 spots")
            already_notified = False

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n  Stopped.")
        sys.exit(0)

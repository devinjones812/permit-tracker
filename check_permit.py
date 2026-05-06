#!/usr/bin/env python3
"""Pretty terminal display for permit availability."""

import sys
from datetime import datetime
from permit_api import check_permit, get_division_name, PERMIT_ID

TARGET_DIVISION = "44585917"
TARGET_DATE = "2026-05-09"
GROUP_SIZE = 3


def display(result: dict):
    date = result["date"]
    group = result["group_size"]
    target = result["division_id"]
    payload = result["payload"]

    print(f"\n{'='*60}")
    print(f"  Yosemite Wilderness Permit Availability Check")
    print(f"{'='*60}")
    print(f"  Date:       {date} ({datetime.strptime(date, '%Y-%m-%d').strftime('%A, %B %d')})")
    print(f"  Trailhead:  {result['division_name']}")
    print(f"  Group size: {group}")
    print(f"{'='*60}\n")

    if result["available"]:
        print(f"  ✅ AVAILABLE! {result['remaining']}/{result['total']} spots remaining")
        print(f"     You need {group} — go book it now!")
        print(f"     {result['booking_url']}")
    elif result["remaining"] > 0:
        print(f"  ⚠️  Only {result['remaining']}/{result['total']} spots remaining (need {group})")
        print(f"     Not enough for your group size.")
    else:
        print(f"  ❌ NO AVAILABILITY")
        print(f"     0 spots remaining for this trailhead on {date}.")

    # Nearby dates with availability
    print(f"\n{'─'*60}")
    print(f"  Nearby dates with availability for this trailhead:")
    print(f"{'─'*60}")

    found_any = False
    for d in sorted(payload.keys()):
        if target in payload[d]:
            info = payload[d][target]
            if info["remaining"] > 0:
                found_any = True
                dt = datetime.strptime(d, "%Y-%m-%d")
                flag = " ← your date" if d == date else ""
                enough = "✅" if info["remaining"] >= group else "⚠️ "
                print(f"    {enough} {dt.strftime('%a %b %d')}: {info['remaining']}/{info['total']} remaining{flag}")

    if not found_any:
        print(f"    None found this month.")

    # Other available trailheads on target date
    print(f"\n{'─'*60}")
    print(f"  Other available trailheads on {date}:")
    print(f"{'─'*60}")

    day_data = payload.get(date, {})
    if day_data:
        for div_id in sorted(day_data.keys()):
            if div_id == target:
                continue
            info = day_data[div_id]
            if info["remaining"] > 0:
                name = get_division_name(div_id)
                enough = "✅" if info["remaining"] >= group else "⚠️ "
                print(f"    {enough} {name}: {info['remaining']}/{info['total']}")
    else:
        print(f"    No data for this date.")

    print()


def main():
    try:
        result = check_permit(TARGET_DATE, TARGET_DIVISION, GROUP_SIZE)
    except Exception as e:
        print(f"  ERROR: {e}")
        sys.exit(1)

    display(result)


if __name__ == "__main__":
    main()

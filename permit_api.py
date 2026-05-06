"""Core API logic for checking Yosemite wilderness permit availability."""

import calendar
import requests

PERMIT_ID = "445859"
API_URL = f"https://www.recreation.gov/api/permitinyo/{PERMIT_ID}/availability"
BOOKING_URL = f"https://www.recreation.gov/permits/{PERMIT_ID}"

DIVISIONS = {
    "44585901": "Happy Isles to Illilouette (no Donohue Pass)",
    "44585902": "Happy Isles to Illilouette (no Donohue Pass)",
    "44585903": "Yosemite Falls",
    "44585904": "Mirror Lake to Snow Creek",
    "44585905": "Yosemite Falls (alt)",
    "44585908": "Pohono Trail (Wawona Tunnel/Bridalveil)",
    "44585909": "Old Big Oak Flat Road",
    "44585910": "Glacier Point to LYV",
    "44585912": "Glacier Point to Illilouette",
    "44585913": "Rockslides (cross-country)",
    "44585916": "Chilnualna Falls",
    "44585917": "Happy Isles to Little Yosemite Valley (no Donohue Pass)",
    "44585918": "Happy Isles to Past LYV (Donohue Pass Eligible)",
    "44585923": "Alder Creek",
    "44585926": "Deer Camp",
    "44585927": "Ostrander (Lost Bear Meadow)",
    "44585928": "Mono Meadow",
    "44585929": "Pohono Trail (Glacier Point)",
    "44585933": "McGurk Meadow",
    "44585934": "Bridalveil Creek",
    "44585935": "Westfall Meadow",
    "44585936": "Pohono Trail (Taft Point)",
    "44585937": "Glacier Point to Illilouette",
    "44585938": "Beehive Meadows",
    "44585941": "Rancheria Falls",
    "44585942": "Miguel Meadow",
    "44585943": "Poopenaut Valley",
    "44585948": "Mather Ranger Station",
    "44585954": "Smith Peak",
    "44585967": "Cottonwood Creek",
    "44585968": "Base Line Camp Road",
    "44585969": "Aspen Valley (Hetch Hetchy)",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def get_division_name(division_id: str) -> str:
    return DIVISIONS.get(division_id, f"Unknown ({division_id})")


def fetch_availability(date: str) -> dict:
    """Fetch permit availability for the entire month containing `date`.

    Returns the raw payload dict: { "YYYY-MM-DD": { "division_id": { "total": N, "remaining": N, ... } } }
    """
    year, month = int(date[:4]), int(date[5:7])
    start = f"{year}-{month:02d}-01"
    last = calendar.monthrange(year, month)[1]
    end = f"{year}-{month:02d}-{last}"

    params = {
        "start_date": start,
        "end_date": end,
        "commercial_acct": "false",
    }
    resp = requests.get(API_URL, params=params, headers=HEADERS)
    resp.raise_for_status()
    return resp.json().get("payload", {})


def check_permit(date: str, division_id: str, group_size: int) -> dict:
    """Check availability for a specific trailhead/date/group size.

    Returns:
        {
            "available": bool,       # True if remaining >= group_size
            "remaining": int,        # spots left (0 if not in response)
            "total": int | None,     # total quota (None if not in response)
            "date": str,
            "division_id": str,
            "division_name": str,
            "group_size": int,
            "booking_url": str,
        }
    """
    payload = fetch_availability(date)
    day_data = payload.get(date, {})
    division_info = day_data.get(division_id)

    if division_info:
        remaining = division_info["remaining"]
        total = division_info["total"]
    else:
        remaining = 0
        total = None

    return {
        "available": remaining >= group_size,
        "remaining": remaining,
        "total": total,
        "date": date,
        "division_id": division_id,
        "division_name": get_division_name(division_id),
        "group_size": group_size,
        "booking_url": BOOKING_URL,
        "payload": payload,
    }

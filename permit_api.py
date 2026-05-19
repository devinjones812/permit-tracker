"""Generic recreation.gov permit availability API."""

import calendar
import requests

API_URL = "https://www.recreation.gov/api/permitinyo/{permit_id}/availability"
BOOKING_URL = "https://www.recreation.gov/permits/{permit_id}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def fetch_availability(permit_id: str, date: str) -> dict:
    """Fetch permit availability for the entire month containing `date`.

    Returns the raw payload dict:
        { "YYYY-MM-DD": { "division_id": { "total": N, "remaining": N, ... } } }
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
    url = API_URL.format(permit_id=permit_id)
    resp = requests.get(url, params=params, headers=HEADERS)
    resp.raise_for_status()
    return resp.json().get("payload", {})


def check_permit(permit_id: str, date: str, division_id: str, group_size: int) -> dict:
    """Check availability for a specific permit/trailhead/date/group size.

    Returns:
        {
            "available": bool,
            "remaining": int,
            "total": int | None,
            "date": str,
            "permit_id": str,
            "division_id": str,
            "group_size": int,
            "booking_url": str,
        }
    """
    payload = fetch_availability(permit_id, date)
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
        "permit_id": permit_id,
        "division_id": division_id,
        "group_size": group_size,
        "booking_url": BOOKING_URL.format(permit_id=permit_id),
    }

"""
What permits to watch. Edit this list, push, and Railway redeploys.

Each watch needs:
    name        - friendly label (shows up in notifications)
    permit_id   - recreation.gov permit ID (from the URL)
    division_id - specific entry/trailhead (sniff from API or DevTools)
    date        - YYYY-MM-DD
    group_size  - how many spots you need
"""

WATCHES = [
    {
        "name": "Mt Whitney Overnight",
        "permit_id": "445860",
        "division_id": "166",
        "date": "2026-05-22",
        "group_size": 1,
    },
]

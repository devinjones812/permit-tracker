# permit-tracker

Monitors recreation.gov permit availability and sends push notifications via [ntfy.sh](https://ntfy.sh) when spots open up.

## How it works

Polls the recreation.gov API every 60 seconds for each permit in `watches.py`. When availability appears, sends an urgent push notification with a direct booking link.

## Usage

1. Edit `permit_tracker/watches.py` with the permits you want to track
2. Push to GitHub — Railway auto-deploys
3. Get notified on your phone when spots open

## Adding a new permit watch

Find your permit on recreation.gov, note the permit ID from the URL (`/permits/{id}`), then use the API to find the division ID:

```
curl "https://www.recreation.gov/api/permitinyo/{PERMIT_ID}/availability?start_date=YYYY-MM-01&end_date=YYYY-MM-31&commercial_acct=false"
```

Add an entry to `permit_tracker/watches.py`:

```python
{
    "name": "Your Permit Name",
    "permit_id": "123456",
    "division_id": "789",
    "date": "2026-06-15",
    "group_size": 2,
},
```

## Project structure

```
permit-tracker/
├── permit_tracker/
│   ├── __init__.py
│   ├── api.py          ← generic recreation.gov API client
│   ├── notify.py       ← ntfy.sh push notification logic
│   ├── watches.py      ← what to monitor (edit this)
│   └── monitor.py      ← polling loop, deploy notif, 12h heartbeat
├── Dockerfile
├── railway.toml
├── requirements.txt
└── README.md
```

## Environment variables (set on Railway)

| Variable | Required | Description |
|----------|----------|-------------|
| `NTFY_TOPIC` | No | ntfy.sh topic (default: `dj-permit-watch-2026`) |
| `NTFY_TOKEN` | No | ntfy.sh auth token for higher rate limits |

## Local development

```bash
python3 -m permit_tracker.monitor          # run the monitor
python3 -m permit_tracker.monitor --test   # send a test notification
```

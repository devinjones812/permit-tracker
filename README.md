# permit-tracker

Monitors recreation.gov permit availability and sends push notifications via [ntfy.sh](https://ntfy.sh) when spots open up.

## How it works

`monitor.py` polls the recreation.gov API every 60 seconds for each permit in `watches.py`. When availability appears, it sends an urgent push notification with a direct booking link.

## Usage

1. Edit `watches.py` with the permits you want to track
2. Push to GitHub — Railway auto-deploys
3. Get notified on your phone when spots open

## Adding a new permit watch

Find your permit on recreation.gov, note the permit ID from the URL (`/permits/{id}`), then use the API to find the division ID:

```
curl "https://www.recreation.gov/api/permitinyo/{PERMIT_ID}/availability?start_date=YYYY-MM-01&end_date=YYYY-MM-31&commercial_acct=false"
```

Add an entry to `watches.py`:

```python
{
    "name": "Your Permit Name",
    "permit_id": "123456",
    "division_id": "789",
    "date": "2026-06-15",
    "group_size": 2,
},
```

## Files

| File | Purpose |
|------|---------|
| `watches.py` | What to monitor — edit this to change watches |
| `monitor.py` | Polling loop, deploy notification, 12h heartbeat |
| `permit_api.py` | Generic recreation.gov permit API client |
| `notify.py` | ntfy.sh push notification logic |

## Environment variables (set on Railway)

| Variable | Required | Description |
|----------|----------|-------------|
| `NTFY_TOPIC` | No | ntfy.sh topic (default: `dj-permit-watch-2026`) |
| `NTFY_TOKEN` | No | ntfy.sh auth token for higher rate limits |

FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY permit_tracker/ permit_tracker/

ENV PYTHONUNBUFFERED=1
CMD ["python3", "-m", "permit_tracker.monitor"]

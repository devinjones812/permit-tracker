FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY permit_api.py monitor.py ./

CMD ["python3", "monitor.py"]

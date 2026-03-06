FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ .
CMD ["python", "main.py"]
# rebuild Fri Mar  6 15:02:04 CET 2026
# auto deploy test Fri Mar  6 22:15:37 CET 2026
# trigger Fri Mar  6 22:23:54 CET 2026

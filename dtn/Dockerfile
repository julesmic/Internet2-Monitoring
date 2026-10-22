FROM python:3.10-slim

# python:slim does not ship ping; the exporter needs it to measure latency.
RUN apt-get update \
    && apt-get install -y --no-install-recommends iputils-ping \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir prometheus_client==0.21.1

COPY exporter.py /exporter.py

# Unbuffered output so logs appear immediately in `docker logs`.
CMD ["python", "-u", "/exporter.py"]

FROM python:3.10-slim

RUN pip install prometheus_client

COPY exporter.py /exporter.py

CMD ["python", "/exporter.py"]




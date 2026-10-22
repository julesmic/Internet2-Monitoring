"""Prometheus exporter for a synthetic DTN (Data Transfer Node).

Each DTN container runs this exporter. Every SCRAPE_INTERVAL seconds it pings
an external host and every peer DTN, then publishes the results on /metrics.
"""
import logging
import subprocess
import time

from prometheus_client import Gauge, start_http_server

METRICS_PORT = 80
SCRAPE_INTERVAL = 5
EXTERNAL_TARGET = "1.1.1.1"
DTN_TARGETS = ["dtn-a", "dtn-b", "dtn-c", "dtn-d", "dtn-e"]

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("dtn-exporter")

status = Gauge('dtn_status', 'DTN node status (1 = up)')
latency = Gauge('dtn_latency_ms', f'DTN ICMP latency to {EXTERNAL_TARGET} (ms)')
dtn_to_dtn_latency = Gauge('dtn_to_dtn_latency_ms', 'DTN-to-DTN ICMP latency (ms)', ['target'])
peer_reachable = Gauge('dtn_peer_reachable', 'Whether a peer DTN answered ping (1 = yes, 0 = no)', ['target'])


def ping_latency(host):
    """Return round-trip time to host in ms, or None if it cannot be measured."""
    try:
        output = subprocess.check_output(
            ["ping", "-c", "1", "-W", "1", host],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
    except subprocess.CalledProcessError:
        # Host unreachable or name did not resolve.
        return None
    except FileNotFoundError:
        log.error("ping binary not found; install iputils-ping in the image")
        return None

    for line in output.splitlines():
        if "time=" in line:
            try:
                return float(line.split("time=")[1].split(" ")[0])
            except (IndexError, ValueError):
                log.warning("Could not parse ping output: %s", line)
    return None


if __name__ == '__main__':
    start_http_server(METRICS_PORT)
    log.info("Serving metrics on :%d", METRICS_PORT)
    while True:
        status.set(1)

        result = ping_latency(EXTERNAL_TARGET)
        # NaN rather than a stale value, so dashboards show a gap on failure.
        latency.set(result if result is not None else float("nan"))

        for target in DTN_TARGETS:
            result = ping_latency(target)
            if result is None:
                peer_reachable.labels(target=target).set(0)
                dtn_to_dtn_latency.labels(target=target).set(float("nan"))
            else:
                peer_reachable.labels(target=target).set(1)
                dtn_to_dtn_latency.labels(target=target).set(result)

        time.sleep(SCRAPE_INTERVAL)

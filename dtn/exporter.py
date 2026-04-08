from prometheus_client import start_http_server, Gauge
import time
import subprocess
import os

status = Gauge('dtn_status', 'DTN node status (1 = up)')
latency = Gauge('dtn_latency_ms', 'DTN ICMP latency to 1.1.1.1 (ms)')
dtn_to_dtn_latency = Gauge('dtn_to_dtn_latency_ms', 'DTN-to-DTN ICMP latency (ms)', ['target'])

DTN_TARGETS = ["dtn-a", "dtn-b", "dtn-c", "dtn-d", "dtn-e"]

def ping_latency(host):
    try:
        output = subprocess.check_output(
            ["ping", "-c", "1", "-W", "1", host],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        for line in output.split("\n"):
            if "time=" in line:
                return float(line.split("time=")[1].split(" ")[0])
    except:
        return None

if __name__ == '__main__':
    start_http_server(80)
    while True:
        status.set(1)

        # Latency to 1.1.1.1
        result = ping_latency("1.1.1.1")
        if result is not None:
            latency.set(result)

        # DTN-to-DTN latency
        for target in DTN_TARGETS:
            result = ping_latency(target)
            if result is not None:
                dtn_to_dtn_latency.labels(target=target).set(result)

        time.sleep(5)


#!/usr/bin/env python3
"""
Run a perfSONAR pScheduler trace test inside a Docker container and publish
the result as Prometheus metrics via node_exporter's textfile collector.

This script is intended to be run periodically.
node_exporter will scrape the .prom file and expose the metrics to Prometheus.
"""

import subprocess
import time

# Path watched by node_exporter's textfile collector.
# node_exporter reads any *.prom files in this directory and exposes them as metrics.
OUTPUT_FILE = "/var/lib/node_exporter/textfile_collector/perfsonar.prom"


def run_pscheduler():
    """
    Execute a pScheduler 'trace' task inside the perfSONAR Docker container.

    Command being executed:
        docker exec perfsonar-testpoint pscheduler task trace 8.8.8.8

    Returns:
        (success: bool, output: str)
        - success is True if the command exits with status code 0
        - output is the captured stdout on success, or an error string on failure
    """
    try:
        # Run the docker exec command, capturing stdout/stderr as text.
        result = subprocess.run(
            ["docker", "exec", "perfsonar-testpoint", "pscheduler", "task", "trace", "8.8.8.8"],
            capture_output=True,  # capture stdout/stderr instead of printing to console
            text=True,            # decode stdout/stderr to strings (not bytes)
            timeout=60            # fail if the command takes longer than 60 seconds
        )

        # By convention, return code 0 means success.
        success = (result.returncode == 0)

        # Return stdout for possible logging/inspection (currently not used elsewhere).
        return success, result.stdout

    except Exception as e:
        # Covers: docker not installed, container not running, timeout, permission issues, etc.
        return False, str(e)


def write_metrics(success):
    """
    Write Prometheus metrics in text exposition format.

    Metrics written:
      - perfsonar_last_run_success (gauge): 1 if last run succeeded, else 0
      - perfsonar_last_run_timestamp (gauge): unix timestamp (seconds) of last run

    Args:
        success (bool): whether the most recent pScheduler run succeeded
    """
    # Unix timestamp in seconds for "when did this script last run?"
    timestamp = int(time.time())

    # Overwrite the .prom file each run so the metrics always represent the latest state.
    # node_exporter will scrape this file.
    with open(OUTPUT_FILE, "w") as f:
        # Metric: success/failure flag for last run
        f.write("# HELP perfsonar_last_run_success Whether last pscheduler run succeeded\n")
        f.write("# TYPE perfsonar_last_run_success gauge\n")
        f.write(f"perfsonar_last_run_success {1 if success else 0}\n")

        # Metric: timestamp of last run (useful to detect if the job has stalled)
        f.write("# HELP perfsonar_last_run_timestamp Unix timestamp of last run\n")
        f.write("# TYPE perfsonar_last_run_timestamp gauge\n")
        f.write(f"perfsonar_last_run_timestamp {timestamp}\n")


if __name__ == "__main__":
    # Run the trace test inside the perfSONAR container
    success, output = run_pscheduler()

    # Publish the result as Prometheus metrics
    write_metrics(success)

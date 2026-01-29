# Deployment and Configuration of an Internet2-Inspired Global Network Monitoring and orchestration Tool

## Overview

This project builds a reproducible, locally deployable network monitoring and orchestration environment inspired by Internet2. It integrates perfSONAR, Prometheus, Grafana, and Ansible on Ubuntu 25.10 ARM64, designed for academic experimentation and performance analysis. This is developed as part of my final-year dissertation at Oxford Brookes University.

## Project Goals

• Deploy a lightweight perfSONAR testpoint using Docker
• Collect and visualise network metrics with Prometheus and Grafana
• Automate setup and configuration with Ansible
• Document all steps for reproducibility 

## Stack Overview

perfSONAR - Network measurement toolkit deployed in Docker
Prometheus - Metrics collection and scraping installed and deployed locally
Grafana - Dashboard and visualisation installed and deployed locally
Ansible - Automation and reproducibility installed and deployed locally

## Installation Steps

1. Docker:

sudo apt update
sudo apt install docker.io -y
sudo usermod -aG docker $USER

2. perfSONAR Testpoint (Docker)

docker run -d \
  --name perfsonar-testpoint \
  --restart unless-stopped \
  perfsonar/testpoint

3. Prometheus

sudo apt install prometheus -y

4. Grafana (with secure keyring setup)

sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://packages.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null
echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://packages.grafana.com/oss/deb stable main" | \
  sudo tee /etc/apt/sources.list.d/grafana.list > /dev/null
sudo apt update
sudo apt install grafana -y
sudo systemctl enable --now grafana-server


## Prometheus Configuration

sudo nano /etc/prometheus/prometheus.yml

## Edit /etc/prometheus/prometheus.yml to include:

global:
  scrape_interval:     15s # Set the scrape interval to every 15 seconds. Default is every 1 minu>
  evaluation_interval: 15s # Evaluate rules every 15 seconds. The default is every 1 minute.
  # scrape_timeout is set to the global default (10s).

  # Attach these labels to any time series or alerts when communicating with
  # external systems (federation, remote storage, Alertmanager).
  external_labels:
      monitor: 'example'

# Alertmanager configuration
alerting:
  alertmanagers:
  - static_configs:
    - targets: ['localhost:9093']

# Load rules once and periodically evaluate them according to the global 'evaluation_interval'.
rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

# A scrape configuration containing exactly one endpoint to scrape:
# Here it's Prometheus itself.

scrape_configs:
  # The job name is added as a label `job=<job_name>` to any timeseries scraped from this config.
  - job_name: 'prometheus'

    # Override the global default and scrape targets from this job every 5 seconds.
    scrape_interval: 5s
    scrape_timeout: 5s

    # metrics_path defaults to '/metrics'
    # scheme defaults to 'http'.

    static_configs:
      - targets: ['localhost:9090']

  - job_name: node
    # If prometheus-node-exporter is installed, grab stats about the local
    # machine by default.
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'perfsonar'
    static_configs:
      - targets: ['172.17.0.2:9595']



Restart Prometheus:

sudo systemctl restart prometheus
sudo systemctl status prometheus

If status is active/running, then in your browser Go to: http://localhost:9090/targets. You should see a new target under job perfsonar. Ideally status: UP.


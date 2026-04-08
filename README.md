# Deployment and Configuration of an Internet2 Global Network Monitoring and Orchestration Tool.

**A reproducible, containerised monitoring lab** demonstrating multi‑protocol probing, distributed DTN node monitoring, and real‑time visualisation using Prometheus, Grafana, and lightweight DTN exporters.

---

## Project Summary

This repository implements a compact, monitoring stack intended for research and teaching. It demonstrates:

- **Active probing** of external services (ICMP, DNS, HTTP, TLS) via Prometheus Blackbox Exporter.  
- **Synthetic DTN nodes** exposing availability and latency metrics.  
- **Centralised collection** with Prometheus and **visualisation** with Grafana.  
- **Docker Compose** orchestration for reproducible deployment and easy extension.

---

## Architecture Overview

The system is organised into four logical layers:

- **Monitoring Core**: Prometheus (scrape and storage) and Grafana (visualisation).  
- **Blackbox Probing Layer**: Blackbox Exporter modules for ICMP, DNS, HTTP, TLS.  
- **DTN Layer**: containerised DTN exporters exposing `dtn_status` and `dtn_latency_ms`.  
- **Presentation Layer**: provisioned Grafana dashboard `Internet2 Monitoring Dashboard`.

Prometheus scrapes both the Blackbox Exporter and each DTN exporter. Grafana is provisioned to load the dashboard automatically from `grafana/dashboards`.

---

## Repository Layout

<img width="1140" height="816" alt="image" src="https://github.com/user-attachments/assets/806ec98b-e1a0-416e-8702-dde90b463078" />


---

## Quick Start

1. **Clone the repository** 

   git clone https://github.com/julesmic/internet2-monitoring.git

   cd internet2-monitoring

2. **Start the stack**
   
   sudo docker-compose up -d

3. **Open Grafana**
URL: http://localhost:3000
Default credentials: admin / admin (change password when prompted)
The dashboard is provisioned as **Internet2 Monitoring Dashboard**.


---

## Configuration Notes

1. Prometheus: edit prometheus/prometheus.yml to add or remove scrape targets.

2. Blackbox: edit blackbox/blackbox.yml to change probe modules and targets.

3. Grafana: dashboards are in grafana/dashboards; provisioning files are in grafana/provisioning.

4. DTN exporter: dtn/exporter.py exposes dtn_status and dtn_latency_ms on /metrics.


---

## Extending the Lab

-- Add DTN nodes by copying dtn/, updating docker-compose.yml, and adding scrape targets.
-- Add probe targets by editing blackbox/blackbox.yml and Prometheus jobs.
-- Add panels by editing grafana/dashboards/internet2-dashboard.json.

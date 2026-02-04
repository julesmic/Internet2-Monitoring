# Deployment and Configuration of an Internet2-Inspired Global Network Monitoring and Orchestration Tool

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

## Environment Setup

## Virtual Manager:
The tool can be set up on Windows OS or MacOS by using Oracle VirtualBox Manager or UTM Virtual Machine respectively. 

## Download Ubuntu image:
Since this is being set up on a MacOS, download Ubuntu 25.10 Desktop iso (ubuntu-25.10-desktop-arm64.iso) for a Graphical User Interface (GUI). 

## Create a new VM in UTM:
Open UTM
Click Create a New Virtual Machine
Choose Virtualize (not Emulate)
Select Linux

## Configure the VM:
System Architecture: ARM64 (aarch64)
Memory: 4096 MB (4 GB)
CPU cores: 4 (or more for better performance)

Enable:
Hardware Virtualization
Force Multicore
UEFI Boot
Drives

UTM will prompt you to add a boot ISO:
Add the Ubuntu 25.10 ARM64 ISO
Create a new virtual disk:
Size: 64 GB recommended
Interface: NVMe (faster) or VirtIO

## Boot the VM:
Start the VM. You’ll see the Ubuntu installer.
If using the desktop ISO, choose:
“Try or Install Ubuntu”
Then “Install Ubuntu”
If using the server ISO, you’ll get the text-based installer.

## Install Ubuntu:
The installer will walk through:
Keyboard layout
Networking
Disk setup (choose “Erase disk and install Ubuntu”)
User account creation
Install now

## First boot and post‑install:
Remove the ISO from UTM settings
Install SPICE tools (for better display & clipboard)

sudo apt update
sudo apt install spice-vdagent (for better resolution)

## Prepare the System:
sudo apt upgrade -y
sudo apt install curl wget git net-tools -y 

Docker will be used as a container for perfSONAR, as this is more reliable and reproducible. It will also integrate well with the native installed Prometheus and Grafana.

## Install Docker:
sudo apt update 
sudo apt install docker.io -y
sudo systemctl enable --now docker 
sudo usermod -aG docker $USER (Adds user to Docker group to use without ‘sudo’)

Reboot VM to apply the group change and login again.

## Run the perfSONAR testpoint container - The Measurement Layer:
The container launches a fully functional perfSONAR environment without relying on package repositories, hence more stable. This provides active measurements (One-Way Active Measurement Protocol latency tests and throughput tests), forming the foundation of the monitoring ecosystem.

docker run -d \
  --name perfsonar-testpoint \
  --restart unless-stopped \
  perfsonar/testpoint

perfSONAR is the performance Service-Oriented Network monitoring ARchitecture, a network measurement toolkit designed to provide federated coverage of paths and help to establish end-to-end usage expectations. (perfsonar.net, 2025).

## Logs can be inspected using:
docker logs perfsonar-testpoint

## Validate the container for API, Tools, and Scheduling:
docker exec -it perfsonar-testpoint pscheduler troubleshoot (everything normal)

## Verify the container is running:
docker ps (perfsonar/testpoint should be listed and running) 

## Install Prometheus - The Metrics Layer: 
sudo apt update
sudo apt install prometheus -y

It will start automatically and listen on port 9090.

## Verify Prometheus is listening:
curl http://localhost:9090 (A basic HTML page will show to confirm it’s running).

## Create Prometheus exporter:
A lightweight script (pscheduler_exporter) is created as a Prometheus exporter for perfSONAR. This helps to pull perfSONAR data from inside the Docker container and expose it to Prometheus in a standard format. It runs pscheduler tasks inside the container, extracts key metrics (e.g., task count, duration, errors), and writes them to a Prometheus-readable format.

Since the Docker container doesn’t expose metrics:

Use pscheduler CLI inside the container to run diagnostic tasks
Parse the results (e.g., latency, throughput, success/failure)
Push them to Prometheus using a custom exporter or node exporter textfile collector

Creating pscheduler_exporter:
Create the Exporter Directory
cd ~/internet2-monitoring
mkdir -p setup/exporter
Create the Exporter Script (Python)
nano setup/exporter/pscheduler_exporter.py
Write the script in an IDE of choice, then paste it in pscheduler_exporter.py.
Test the script manually:
python3 /home/jules/internet2-monitoring/setup/exporter/pscheduler_exporter.py
It should create a file in this location: /var/lib/node_exporter/textfile_collector/perfsonar.prom
Check the location: ls -l /var/lib/node_exporter/textfile_collector/. If perfsonar.prom is there, then the script is working.

Enable Node Exporter’s Textfile Collector: 

Install node exporter:
sudo apt install prometheus-node-exporter -y
Check the collector directory:
ls /var/lib/prometheus/node-exporter/
Create the textfile collector directory:
sudo mkdir -p /var/lib/node_exporter/textfile_collector
Give permissions:
sudo chmod 777 /var/lib/node_exporter/textfile_collector

Add a Cron Job to Run the Exporter:
Open cron: crontab -e
Select Option 1 (/bin/nano) as this is the easiest for quick edits. 
Paste the below into the opened job. This will run the exporter every 5 minutes: 
*/5 * * * * /usr/bin/python3 /home/jules/internet2-monitoring/setup/exporter/pscheduler_exporter.py
Ctrl O and Enter to save, then Crtl X to exit.

Add the Exporter to Prometheus:
sudo nano /etc/prometheus/prometheus.yml

## Install Grafana - The Visualisation Layer:
Add Grafana and its GPG (GNU Privacy Guard) key in binary format to prevent key mismatch: 

GPG key is a pair of cryptographic keys; a public key to encrypt data or verify signatures, and a private key for decrypting data or creating signatures.

sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://packages.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null



## Add the Grafana repository, referencing its keyring:

echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://packages.grafana.com/oss/deb stable main" | \
  sudo tee /etc/apt/sources.list.d/grafana.list > /dev/null

## Update and install Grafana:

sudo apt update
sudo apt install grafana -y
sudo systemctl enable --now grafana-server

## Access Grafana:
Open http://localhost:3000 on web browser
Username: admin
Password: admin (change this to yours when prompted)

## Connect Prometheus to perfSONAR container:
Find the container’s IP address:

docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' perfsonar-testpoint
IP address: 172.17.0.2


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



Restart Prometheus for functionality:

sudo systemctl restart prometheus
sudo systemctl status prometheus

If status is active/running, then in your browser Go to: http://localhost:9090/targets. Navigate to Staus and select Targets in the dropdown menu, you should see prometheus and node_exporter states as UP. This means that Prometheus is scraping itself correctly on localhost:9090 and scraping the node exporter on localhost:9100.
The system metrics are being collected.
The textfile collector (where your perfSONAR exporter will write metrics) is available.
Prometheus is healthy and scraping on schedule.





## Build Grafana dashboards:



## Create Ansible playbooks for reproducibility: 
Ansible allows automation of the whole stack.









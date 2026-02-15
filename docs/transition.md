# Transition from original monitoring stack to new approach

## Summary
This document records why the project moved from the original Prometheus + Grafana + perfSONAR setup to a new architecture, and where to find the archived work.

## Why the change
- **Scope shift**: There was a continuous issue with scraping metrics from perfSONAR to prioritise, hence the shift to not use it anymore and have a functional product.
- **Maintainability**: The original stack required manual provisioning that hindered reproducibility.
- **Experimentation**: The new approach explores container-native telemetry and automated provisioning.

## Where the legacy work lives
- Branch: `legacy`
- Tag: `v1-legacy`
- Key artifacts: `setup/configs/prometheus.yml`, Grafana provisioning files, commit history documenting stepwise changes.

## How to reproduce legacy environment
1. Checkout legacy branch: `git checkout legacy`
2. Review `setup/` and `docs/` for configuration and installation notes
3. Optional: request VM artifact (OVA) referenced in `docs/artifacts.md` if available

## New approach workflow
- Branch for experiments: `project/new-approach`
- Keep commits small and descriptive; push frequently
- Merge stable changes into `main`


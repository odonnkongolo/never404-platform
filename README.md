# 🚀 never404-platform: Automated GitOps & Observability Cluster
# 📌 Overview
This repository contains the Infrastructure as Code (IaC), Continuous Integration/Continuous Deployment (CI/CD) pipelines, and application manifests for the never404.co.uk platform.

The project is built around a "Shift-Left" security philosophy and an immutable GitOps architecture, deploying a containerized Python application (Market Tracker) to an AWS Kubernetes cluster with fully automated TLS routing and enterprise observability.

Live Endpoints:

Main Application: https://never404.co.uk (Streamlit Python App)

SRE Cockpit: https://grafana.never404.co.uk (Prometheus/Grafana)

# 🏗️ Architecture Stack
Cloud Provider: AWS (EC2 t3.small / VPC / Security Groups)

Infrastructure as Code (IaC): Terraform

Orchestration: K3s (Lightweight Kubernetes)

Ingress & Networking: Traefik + Cert-Manager (Let's Encrypt TLS)

CI/CD: GitHub Actions (Decoupled Integration & Deployment)

Container Registry: GitHub Container Registry (GHCR)

Observability: kube-prometheus-stack (Helm)

Application: Python 3.11 / Streamlit

# ⚙️ CI/CD Pipeline Design
The GitHub Actions pipeline .github/workflows/deploy.yaml is intentionally decoupled into two distinct jobs to isolate the blast radius of code failures from live infrastructure:

Job 1: Continuous Integration (CI Gatekeepers)

Code is checked out into an isolated Ubuntu runner.

Ruff: Executes blazing-fast static code analysis and syntax linting.

Bandit: Scans for high-severity security vulnerabilities (e.g., hardcoded secrets, injection flaws).

The pipeline strictly halts here if any vulnerability or syntax error is detected, protecting the live production environment.

Job 2: Continuous Deployment (AWS Rollout)

Depends entirely on a successful CI pass.

Builds the Python app into a Docker container and pushes it to GHCR.

Injects highly-scoped temporary Kubeconfig credentials.

Executes a GitOps pull, applying the latest YAML manifests to the live K3s cluster.

# 🛠️ Infrastructure & SRE Runbook
The Bootstrap (user_data)
The AWS cluster is provisioned via Terraform. The main.tf file contains a highly customized user_data bootstrap script engineered to bypass common cloud-native bottlenecks:

SRE Hotfix 1: MTU Packet Fragmentation: AWS applies a 9001 MTU limit, while standard Docker/Flannel networks expect 1500. This mismatch causes silent TLS handshake timeouts during deployments. The bootstrap script permanently injects iptables TCPMSS --clamp-mss-to-pmtu rules to force packet alignment.

SRE Hotfix 2: OOM API Crashes: The kube-prometheus-stack is resource-intensive. To prevent the K3s API from suffocating on a 2GB RAM instance, the bootstrap uses dd to physically write a bulletproof 2GB /swapfile to the disk prior to cluster initialization.

Traffic Routing
Traefik acts as the cluster receptionist, routing traffic based on hostname rules (Ingress).

Cert-Manager automatically interfaces with Let's Encrypt to provision, rotate, and manage SSL/HTTPS certificates without human intervention.

Internal routing to Grafana is locked behind a strict HTTPS-only entrypoint annotation.

# 🚨 Known Resource Constraints
The t3.small instance operates with 2GB of active RAM. Running a full enterprise observability suite alongside an application and an ingress controller maxes out system memory, occasionally triggering the Linux OOM Killer (Out Of Memory).

Emergency Amputation Playbook (To restore main app routing):
If the cluster drops external traffic due to CoreDNS or Traefik starvation:

Bash
# 1. Uninstall the heavy monitoring suite
helm uninstall prometheus --namespace monitoring

# 2. Restart core routing services
kubectl delete pod -n kube-system -l k8s-app=kube-dns
kubectl delete pod -n kube-system -l app.kubernetes.io/name=traefik

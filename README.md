# 🚀 never404-platform: Automated GitOps & Observability Cluster

## 📌 Overview

This repository contains the Infrastructure as Code (IaC), Continuous Integration/Continuous Deployment (CI/CD) pipelines, and application manifests for the never404.co.uk platform.

The project is built around a "Shift-Left" security philosophy and an immutable GitOps architecture, deploying a containerized Python application (Market Tracker) to an AWS Kubernetes cluster with fully automated TLS routing and enterprise observability.

**Live Endpoints:**

- Main Application: [https://never404.co.uk](https://never404.co.uk) (Streamlit Python App)
- SRE Cockpit: [https://grafana.never404.co.uk](https://grafana.never404.co.uk) (Prometheus/Grafana)

---

## 🏗️ Architecture Stack

| Layer | Technology |
|---|---|
| Cloud Provider | AWS (EC2 t3.small / VPC / Security Groups) |
| Infrastructure as Code | Terraform |
| Configuration Management | Ansible |
| Orchestration | K3s (Lightweight Kubernetes) |
| Ingress & Networking | Traefik + Cert-Manager (Let's Encrypt TLS) |
| CI/CD | GitHub Actions (4-Stage Decoupled Dependency Graph) |
| Container Registry | GitHub Container Registry (GHCR) |
| Observability | kube-prometheus-stack (Helm) |
| Application | Python 3.11 / Streamlit |

---

## ⚙️ CI/CD Pipeline Design

The GitHub Actions pipeline `.github/workflows/deploy.yaml` uses a strict dependency graph decoupled into four distinct stages. This isolates the blast radius of code failures from live infrastructure, ensuring bad code or syntax never reaches the server:

### Stage 1: APP CI (Python Gatekeepers)
- **Ruff:** Executes blazing-fast static code analysis and syntax linting.
- **Bandit:** Scans for high-severity security vulnerabilities (e.g., hardcoded secrets, injection flaws).

### Stage 2: INFRA CI (Ansible Gatekeepers)
- **Ansible-Lint:** Enforces strict YAML formatting, FQCN (Fully Qualified Collection Name) compliance, and idempotency rules on the infrastructure playbooks.

### Stage 3: INFRA CD (Server Configuration)
- Unlocks only if Stage 1 & 2 pass.
- Injects secured SSH keys and executes an idempotent Ansible playbook against the live AWS instance to configure memory limits, network gates, and the K3s engine.

### Stage 4: APP CD (Kubernetes Deployment)
- Unlocks only if Stage 3 passes.
- Builds the Python app into a Docker container and pushes it to GHCR.
- Orchestrates a safe pre-flight installation of Cert-Manager CRDs.
- Executes a GitOps pull, applying the latest YAML manifests to the live K3s cluster.

---

## 🛠️ Infrastructure & SRE Runbook

### Enterprise Configuration Management (Ansible)

The infrastructure is provisioned completely bare via Terraform, and then declaratively configured via Ansible (`ansible/setup-cluster.yaml`) to bypass common cloud-native bottlenecks:

- **SRE Hotfix 1 — MTU Packet Fragmentation:** AWS applies a 9001 MTU limit, while standard Docker/Flannel networks expect 1500. This mismatch causes silent TLS handshake timeouts during deployments. Ansible dynamically injects `iptables TCPMSS --clamp-mss-to-pmtu` rules to force packet alignment.

- **SRE Hotfix 2 — OOM API Crashes:** The kube-prometheus-stack is resource-intensive. To prevent the K3s API from suffocating on a 2GB RAM instance, Ansible uses the native `lineinfile` and `dd` modules to physically write a bulletproof 2GB `/swapfile` to the disk prior to cluster initialization.

- **SRE Hotfix 3 — TLS SAN Verification:** To prevent external `kubectl` timeouts, Ansible dynamically extracts the AWS public IP and injects it into `/etc/rancher/k3s/config.yaml` as a trusted Subject Alternative Name.

### Traffic Routing & Pre-Flight Checks

- **Cert-Manager Race Conditions:** To prevent CRD mapping errors, the pipeline explicitly uses `kubectl wait` to ensure the `cert-manager-webhook` is fully awake and listening before applying the Let's Encrypt `ClusterIssuer`.
- **Traefik** acts as the cluster receptionist, routing traffic based on hostname rules (Ingress).
- Internal routing to Grafana is locked behind a strict HTTPS-only entrypoint annotation, with namespaces provisioned idempotently.

---

## 🚨 Known Resource Constraints

The t3.small instance operates with 2GB of active RAM. Running a full enterprise observability suite alongside an application and an ingress controller maxes out system memory, occasionally triggering the Linux OOM Killer (Out Of Memory).

### Emergency Amputation Playbook

If the cluster drops external traffic due to CoreDNS or Traefik starvation:

```bash
# 1. Uninstall the heavy monitoring suite
helm uninstall prometheus --namespace monitoring

# 2. Restart core routing services
kubectl delete pod -n kube-system -l k8s-app=kube-dns
kubectl delete pod -n kube-system -l app.kubernetes.io/name=traefik
```

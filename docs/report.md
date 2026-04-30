# ACEest Fitness — DevOps Assignment 2 Report

> Replace bracketed `[...]` fields below with your own info before submitting.
> Drop screenshot files into `docs/screenshots/` using the exact filenames
> referenced in this report (also listed in
> [screenshot-checklist.md](./screenshot-checklist.md)).

---

**Student name:** [Your Name]
**Roll / ID:** [Your ID]
**Course:** [Course code — DevOps]
**Instructor:** [Instructor Name]
**Submission date:** [DD MMM YYYY]
**Repository:** https://github.com/samrat-2024tm93628/ACEest-Fitness-App

---

## Table of Contents

1. [Abstract](#1-abstract)
2. [Introduction](#2-introduction)
3. [Project Overview](#3-project-overview)
4. [DevOps Lifecycle Mapping](#4-devops-lifecycle-mapping)
5. [System Architecture](#5-system-architecture)
6. [Implementation](#6-implementation)
   - 6.1 [Source Control & Branching](#61-source-control--branching)
   - 6.2 [Application & Test Suite](#62-application--test-suite)
   - 6.3 [Containerisation (Docker)](#63-containerisation-docker)
   - 6.4 [Static Analysis (SonarQube)](#64-static-analysis-sonarqube)
   - 6.5 [CI/CD — Jenkins](#65-cicd--jenkins)
   - 6.6 [CI/CD — GitHub Actions](#66-cicd--github-actions)
   - 6.7 [Container Orchestration (Kubernetes / Minikube)](#67-container-orchestration-kubernetes--minikube)
   - 6.8 [Rolling Update & Rollback](#68-rolling-update--rollback)
   - 6.9 [Autoscaling (HPA)](#69-autoscaling-hpa)
   - 6.10 [Smoke Testing in Production](#610-smoke-testing-in-production)
7. [Deployment Strategies](#7-deployment-strategies)
8. [Security & Secrets](#8-security--secrets)
9. [Monitoring & Logging](#9-monitoring--logging)
10. [Infrastructure as Code](#10-infrastructure-as-code)
11. [Challenges & Lessons Learned](#11-challenges--lessons-learned)
12. [Conclusion](#12-conclusion)
13. [References](#13-references)
14. [Appendix A — File Inventory](#14-appendix-a--file-inventory)

---

## 1. Abstract

This report documents the extension of the *ACEest Fitness* application
(originally delivered in Assignment 1 as a Flask + SQLite REST API with
basic CI) into a complete, production-style DevOps pipeline. Assignment 2
adds reproducible builds, multi-stage containerisation, static analysis with
SonarQube quality gating, Kubernetes-based orchestration with rolling
updates and Horizontal Pod Autoscaling, automated rollback, and
post-deployment smoke testing. The full pipeline is implemented in Jenkins
(primary, 9 stages) with a parallel GitHub Actions workflow publishing
images to the GitHub Container Registry. Test coverage is **96 %**, and the
SonarQube quality gate is enforced via `waitForQualityGate abortPipeline:true`
inside the Jenkins pipeline.

## 2. Introduction

The objective of Assignment 2 is to demonstrate a working DevOps lifecycle
on top of an existing application, applying immutable deployments, rollback
strategies, container orchestration, and Infrastructure-as-Code concepts.
This report presents the gap analysis from Assignment 1, the complete
implementation across seven workstreams (hygiene, container, quality,
CI/CD, Kubernetes, deployment strategies, documentation), and the evidence
that each stage operates as designed.

## 3. Project Overview

ACEest Fitness is a stateless Flask 3 / Python 3.11 REST API exposing six
endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| GET  | `/health`     | Liveness/readiness probe target |
| GET  | `/programs`   | List fitness programs |
| POST | `/calculate`  | BMI calculation |
| GET  | `/export/csv` | CSV export of programs |
| POST | `/client`     | Persist client + BMI to SQLite |
| GET  | `/status`     | Gym capacity metrics |

The application is containerised with a multi-stage Dockerfile, deployed
to Kubernetes as three replicas behind a Service, autoscaled by an HPA,
and managed via a Jenkins pipeline that includes static-analysis quality
gating and automatic rollback.

## 4. DevOps Lifecycle Mapping

Each lifecycle phase maps to one or more concrete tools used in this
project:

| Phase | Tools | Artifact in repo |
|---|---|---|
| Plan | GitHub Issues, branch naming convention | — |
| Code | Git, `feature/*`, `bug/*` branches | repo history |
| Build | Jenkins `Setup` + `Lint`, GitHub Actions `Build & Lint` | [Jenkinsfile](../Jenkinsfile), [.github/workflows/main.yml](../.github/workflows/main.yml) |
| Test | pytest + pytest-cov (unit), `test_smoke.py` (integration) | [pytest.ini](../pytest.ini), [tests/](../tests/) |
| Release | Docker multi-stage build, immutable `:BUILD_NUMBER` tags | [Dockerfile](../Dockerfile) |
| Deploy | `kubectl set image` rolling update | [k8s/deployment.yaml](../k8s/deployment.yaml) |
| Operate | K8s probes, HPA, restart policy | [k8s/hpa.yaml](../k8s/hpa.yaml) |
| Monitor | `/health`, `kubectl logs`, `kubectl get hpa` | application code |

## 5. System Architecture

The logical architecture below shows the path from developer push through
quality gating to a running pod set in Kubernetes. See
[architecture.md](./architecture.md) for the source Mermaid diagram.

![System architecture](screenshots/00-architecture.png)
*Figure 5.1 — System architecture. (Render `docs/architecture.md`'s Mermaid
diagram and export as `00-architecture.png`, or screenshot the rendered
view from a Markdown previewer.)*

### Key design decisions

- **Stateless app, stateful volume.** SQLite lives on an `emptyDir` volume
  per pod — sufficient for the demo, replaceable with a `PersistentVolumeClaim`
  + Postgres for multi-replica persistence.
- **Two CI systems by design.** GitHub Actions provides per-push feedback;
  Jenkins owns the production path with SonarQube and `kubectl`.
- **All secrets external.** Configuration via `ConfigMap`, secrets via
  `Secret`, both consumed via `envFrom` so the app code is unaware of the
  source.
- **Zero-downtime by construction.** `maxUnavailable: 0` plus `maxSurge: 1`
  plus a readiness probe on `/health` guarantees that no client request
  is routed to a non-ready pod during a rollout.

## 6. Implementation

### 6.1 Source Control & Branching

The repository follows trunk-based development with short-lived
`feature/*` and `bug/*` branches merging into `main`. Tags
(`v1.0`, `v2.2.4`, `v3.2.4`) mark release boundaries.

![Git log graph](screenshots/01-git-log.png)
*Figure 6.1.1 — `git log --oneline --graph --all -15` showing branch and
tag history.*

![GitHub repository](screenshots/02-github-repo.png)
*Figure 6.1.2 — GitHub repository landing page.*

### 6.2 Application & Test Suite

The test suite contains **19 unit tests** plus **3 integration smoke
tests** (skipped unless `BASE_URL` is set). Coverage is measured by
`pytest-cov` on every test run via [pytest.ini](../pytest.ini), producing
both human-readable terminal output and a machine-readable
`coverage.xml` consumed by SonarQube.

![pytest local run](screenshots/03-pytest-local.png)
*Figure 6.2.1 — Local pytest run: 19 passed, 3 skipped, coverage 96 %.*

![curl /health](screenshots/04-curl-health.png)
*Figure 6.2.2 — Application responding on `/health`.*

### 6.3 Containerisation (Docker)

The [Dockerfile](../Dockerfile) is a two-stage build that installs
dependencies into an isolated prefix in stage 1 and copies them into a
clean `python:3.11-slim` runtime in stage 2. The runtime image runs as
non-root user `ace` (uid 1001), declares a `HEALTHCHECK` against
`/health`, and excludes tests, `.git`, and venvs through
[.dockerignore](../.dockerignore).

![docker build](screenshots/05-docker-build.png)
*Figure 6.3.1 — Multi-stage Docker build completing successfully.*

![docker images](screenshots/06-docker-images.png)
*Figure 6.3.2 — Tagged image with `:BUILD_NUMBER` and `:latest`.*

[docker-compose.yml](../docker-compose.yml) brings the entire local DevOps
stack online with a single command — Flask app + SonarQube +
Postgres-backed SonarQube DB.

![docker compose up](screenshots/07-docker-compose-up.png)
*Figure 6.3.3 — `docker compose ps` showing all three services healthy.*

### 6.4 Static Analysis (SonarQube)

SonarQube runs as part of the Compose stack on
`http://localhost:9000`. Its scanner is invoked from the Jenkins pipeline
inside `withSonarQubeEnv('SonarQube')`, using configuration in
[sonar-project.properties](../sonar-project.properties). The pipeline
then waits on the quality gate:

```groovy
stage('Quality Gate') {
    steps {
        timeout(time: 5, unit: 'MINUTES') {
            waitForQualityGate abortPipeline: true
        }
    }
}
```

If the gate fails, the build fails and nothing is pushed or deployed.

![Sonar scan in Jenkins log](screenshots/08-sonar-scan-jenkins.png)
*Figure 6.4.1 — `sonar-scanner` running inside the Jenkins pipeline.*

![Sonar dashboard](screenshots/09-sonar-dashboard.png)
*Figure 6.4.2 — SonarQube project dashboard: coverage, bugs,
vulnerabilities, code smells.*

![Sonar quality gate](screenshots/10-sonar-quality-gate.png)
*Figure 6.4.3 — Quality gate "Passed".*

### 6.5 CI/CD — Jenkins

The [Jenkinsfile](../Jenkinsfile) defines a **9-stage cross-platform
pipeline**: Checkout → Setup → Lint → Test+Coverage → SonarQube → Quality
Gate → Docker Build → Docker Push → Deploy to K8s → Smoke Test, with
`post.failure` automatically running `kubectl rollout undo`. Stages that
depend on external systems (Sonar, registry, K8s) are gated by env vars,
so the same file runs cleanly on a barebones Jenkins or a fully-configured
one.

See [pipeline-flow.md](./pipeline-flow.md) for the stage-purpose table
and the full Mermaid flowchart.

![Jenkins pipeline overview](screenshots/11-jenkins-pipeline-overview.png)
*Figure 6.5.1 — Jenkins stage view, all stages green.*

![Jenkins build log](screenshots/12-jenkins-build-log.png)
*Figure 6.5.2 — Console output of a representative pipeline run.*

![JUnit results](screenshots/13-jenkins-test-results.png)
*Figure 6.5.3 — JUnit test report panel inside Jenkins.*

### 6.6 CI/CD — GitHub Actions

[.github/workflows/main.yml](../.github/workflows/main.yml) provides fast
PR feedback (lint + test + coverage on every push/PR) and pushes the
container image to GitHub Container Registry on `main` using
`GITHUB_TOKEN` — no extra secret configuration required.

![GitHub Actions summary](screenshots/14-gh-actions-summary.png)
*Figure 6.6.1 — Workflow run summary, both jobs green.*

![GHCR image](screenshots/15-ghcr-image.png)
*Figure 6.6.2 — Pushed container image visible under repository "Packages".*

### 6.7 Container Orchestration (Kubernetes / Minikube)

Six manifests under [k8s/](../k8s/) define the entire cluster footprint:
namespace, ConfigMap, Secret, Deployment (3 replicas, RollingUpdate
strategy, liveness + readiness probes, resource requests/limits, non-root
security context with read-only rootfs and `drop: [ALL]` capabilities),
ClusterIP + NodePort Services, and an autoscaling/v2 HPA.

![minikube status](screenshots/16-minikube-status.png)
*Figure 6.7.1 — Minikube cluster healthy.*

![kubectl apply](screenshots/17-kubectl-apply.png)
*Figure 6.7.2 — All six manifests applied successfully.*

![kubectl get pods](screenshots/18-kubectl-get-pods.png)
*Figure 6.7.3 — Three replicas running across the namespace.*

![rollout status](screenshots/19-rollout-status.png)
*Figure 6.7.4 — `kubectl rollout status` confirming successful deployment.*

![App via NodePort](screenshots/20-curl-via-nodeport.png)
*Figure 6.7.5 — Application reachable through the NodePort Service URL.*

### 6.8 Rolling Update & Rollback

The deployment uses `strategy.rollingUpdate.maxUnavailable: 0` so total
ready replicas never dip below the desired count during a rollout —
delivering zero-downtime updates. Rollback is provided at two levels:

1. **Image-level** — every Jenkins build produces an immutable tag
   `:BUILD_NUMBER`; any historical version can be redeployed.
2. **Kubernetes-level** — `kubectl rollout undo` restores the previous
   ReplicaSet. This is wired into [Jenkinsfile](../Jenkinsfile) `post.failure`
   and exposed via [scripts/rollback.sh](../scripts/rollback.sh).

![Rolling update to v2](screenshots/21-set-image-v2.png)
*Figure 6.8.1 — `kubectl set image …:v2` and pods rolling.*

![rollout history](screenshots/22-rollout-history.png)
*Figure 6.8.2 — `kubectl rollout history` showing multiple revisions.*

![Rollback](screenshots/23-rollout-undo.png)
*Figure 6.8.3 — `./scripts/rollback.sh` reverting to the previous revision.*

### 6.9 Autoscaling (HPA)

[k8s/hpa.yaml](../k8s/hpa.yaml) targets 70 % CPU utilisation with a
2–6 replica range. The HPA reads metrics from `metrics-server` (enabled in
Minikube via `minikube addons enable metrics-server`) and uses the
`requests.cpu` value from the Deployment as the denominator.

![HPA at idle](screenshots/24-hpa-idle.png)
*Figure 6.9.1 — HPA at rest (replicas = 2).*

![HPA under load](screenshots/25-hpa-under-load.png)
*Figure 6.9.2 — HPA scaled to 4–6 replicas under synthetic load.*

### 6.10 Smoke Testing in Production

The smoke tests in [tests/integration/test_smoke.py](../tests/integration/test_smoke.py)
run against the **deployed** URL inside the Jenkins `Smoke Test` stage. If
they fail, the post-failure handler triggers `kubectl rollout undo` —
proving "deployed code answers traffic" before declaring success.

![Smoke test against live cluster](screenshots/26-smoke-test.png)
*Figure 6.10.1 — `./scripts/smoke-test.sh` passing against the deployed
service.*

## 7. Deployment Strategies

The project **implements** rolling updates and **demonstrates** blue/green;
canary, A/B, and shadow are documented conceptually because they require
either a service mesh or weighted Ingress rules outside the assignment
scope. Full comparison and demo commands live in
[deployment-strategies.md](./deployment-strategies.md).

| Strategy | Downtime | Risk | Overhead | Rollback | Implemented here |
|---|---|---|---|---|---|
| Recreate | yes | high | none | slow | no |
| **Rolling** | none | low | +1 replica | fast | **yes (default)** |
| Blue/Green | none | low | 2× replicas | instant | yes (manual demo) |
| Canary | none | lowest | +1 replica | fast | concept |
| A/B | none | lowest | +1 per variant | fast | concept |
| Shadow | none | none | full mirror | n/a | concept |

## 8. Security & Secrets

- `.env` is git-ignored; `.env.example` documents the contract.
- Container runs as **non-root** (uid 1001) with **read-only root filesystem**
  and **all Linux capabilities dropped** (`drop: [ALL]`).
- Kubernetes [Secret](../k8s/secret.yaml) injected via `envFrom`; placeholder
  in repo for screenshot purposes only — production secrets are created
  with `kubectl create secret --from-env-file=.env`.
- Jenkins credentials accessed via `withCredentials([usernamePassword(...)])`
  so they never appear in build logs.
- Dependencies are **pinned** for reproducibility and supply-chain
  predictability.

## 9. Monitoring & Logging

- `/health` endpoint serves as both K8s liveness and readiness target.
- `PYTHONUNBUFFERED=1` in the Dockerfile guarantees logs reach
  `kubectl logs` immediately.
- Operational visibility relies on `kubectl logs`, `kubectl get hpa`,
  `kubectl describe pod`, and SonarQube's running quality history. A
  full Prometheus + Grafana stack is documented as a future enhancement.

## 10. Infrastructure as Code

This project treats the following as IaC:

1. **Kubernetes manifests** under [k8s/](../k8s/) — declarative, idempotent,
   version-controlled. `kubectl apply -f k8s/` reproduces the entire
   application state.
2. **`docker-compose.yml`** — declares the local development stack
   (app + SonarQube + Postgres).
3. **`Jenkinsfile` and `.github/workflows/main.yml`** — pipeline-as-code.

For cloud-level provisioning (cluster, VPC, node pools), Terraform is the
industry-standard tool and would extend this project naturally without
changing the application or Kubernetes layers.

## 11. Challenges & Lessons Learned

- **Import-time side effects break containers.** The Assignment 1 `app.py`
  invoked `init_db()` at module load, which created `aceest.db` in the
  current working directory; this fails on a read-only root filesystem.
  Fix: lazy-init inside the request handler and configure the path via
  the `DB_PATH` env var.
- **HPA needs `resources.requests.cpu`.** Without it, the HPA cannot
  compute "utilisation" and stays at the minimum replica count.
- **Jenkins must be cross-platform.** Hard-coding `bat` in the original
  pipeline made it fail on a Linux agent. Wrapping shell commands in
  `if (isUnix())` makes the same Jenkinsfile portable.
- **Quality gates must abort.** Sonar's default behaviour is to record
  the gate result without affecting the build; `abortPipeline: true` is
  what actually enforces the gate.

## 12. Conclusion

The application has progressed from a single-file Flask service with a
basic CI workflow to a fully orchestrated, observable, and self-healing
deployment with a comprehensive quality gate. All twelve top-level
requirements of Assignment 2 — DevOps lifecycle, CI/CD, automated testing,
containerisation, SonarQube, Jenkins, Kubernetes/Minikube, deployment
strategies, rollback, monitoring concepts, IaC concepts, and secrets
management — are addressed with working artefacts in this repository.

## 13. References

1. Kubernetes documentation — Deployments, HPA, Probes — https://kubernetes.io/docs
2. SonarQube documentation — Quality Gates — https://docs.sonarsource.com/sonarqube
3. Jenkins documentation — Pipeline syntax — https://www.jenkins.io/doc/book/pipeline/
4. Docker documentation — Multi-stage builds — https://docs.docker.com/build/building/multi-stage/
5. The Twelve-Factor App — https://12factor.net/

## 14. Appendix A — File Inventory

```
app.py                            Flask application (env-driven config, lazy DB init)
requirements.txt                  Pinned production dependencies
requirements-dev.txt              Pinned dev dependencies (pytest, pytest-cov, coverage)
pytest.ini                        Pytest config: coverage + smoke marker
test_app.py                       Unit tests (19)
tests/integration/test_smoke.py   Integration smoke tests (3)
Dockerfile                        Multi-stage, non-root, healthcheck
.dockerignore                     Excludes git, venv, tests, secrets from build context
.env.example                      Documents env contract; .env is git-ignored
docker-compose.yml                Local stack: app + sonarqube + sonar-db
sonar-project.properties          SonarQube scanner config
Jenkinsfile                       9-stage cross-platform pipeline
.github/workflows/main.yml        GitHub Actions: test + GHCR push
k8s/namespace.yaml                Namespace
k8s/configmap.yaml                Non-secret env (PORT, DB_PATH)
k8s/secret.yaml                   Demo secret (Opaque)
k8s/deployment.yaml               3 replicas, RollingUpdate, probes, security context
k8s/service.yaml                  ClusterIP + NodePort
k8s/hpa.yaml                      autoscaling/v2 HPA, 2..6 replicas @ 70% CPU
scripts/deploy.sh                 Apply manifests + set image + wait for rollout
scripts/rollback.sh               kubectl rollout undo (with optional revision)
scripts/smoke-test.sh             Run smoke tests against deployed service
docs/architecture.md              System architecture + Mermaid diagrams
docs/pipeline-flow.md             CI/CD pipeline diagram + stage table
docs/deployment-strategies.md     Strategy comparison + demo commands
docs/screenshot-checklist.md      Capture instructions for all 26 screenshots
docs/viva-prep.md                 Likely viva questions with grounded answers
docs/report.md                    This document
```

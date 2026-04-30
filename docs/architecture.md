# Architecture

ACEest Fitness is a stateless Flask API packaged as an OCI container, deployed
on Kubernetes (Minikube for local demo) with three replicas behind a Service
and an HPA. All build/test/deploy steps are automated via Jenkins; GitHub
Actions provides redundant pre-merge feedback. SonarQube runs in Docker
Compose alongside the app for static analysis and quality gating.

## Logical architecture

```mermaid
flowchart LR
    Dev([Developer]) -->|git push| GH[GitHub Repo]
    GH -->|webhook| GA[GitHub Actions<br/>lint + test + GHCR push]
    GH -->|polled| J[Jenkins]
    J -->|sonar-scanner| SQ[(SonarQube + Postgres)]
    J -->|docker push| REG[(Image Registry<br/>DockerHub / GHCR)]
    J -->|kubectl apply / set image| K8S

    subgraph K8S [Kubernetes Namespace: aceest]
        SVC[Service: aceest<br/>ClusterIP + NodePort 30080]
        HPA[HorizontalPodAutoscaler<br/>2..6 pods @ 70% CPU]
        subgraph DEP [Deployment: aceest replicas=3]
            P1[Pod app:5000<br/>liveness+readiness /health]
            P2[Pod app:5000]
            P3[Pod app:5000]
        end
        CM[ConfigMap aceest-config<br/>PORT, DB_PATH]
        SEC[Secret aceest-secrets<br/>API_KEY]
        SVC --> P1 & P2 & P3
        HPA -.scales.-> DEP
        CM -.envFrom.-> DEP
        SEC -.envFrom.-> DEP
    end

    User([Browser / curl]) -->|HTTP /health, /programs, ...| SVC
```

## Data flow

```mermaid
sequenceDiagram
    autonumber
    actor Dev
    participant Git as GitHub
    participant J as Jenkins
    participant Sonar as SonarQube
    participant Reg as Registry
    participant K as Kubernetes
    Dev->>Git: push commit
    Git->>J: webhook / poll
    J->>J: install deps, pytest --cov
    J->>Sonar: sonar-scanner (coverage.xml)
    Sonar-->>J: Quality Gate result
    J->>J: docker build -t :BUILD
    J->>Reg: docker push :BUILD :latest
    J->>K: kubectl set image (RollingUpdate)
    K-->>J: rollout status (success | failure)
    alt failure
        J->>K: kubectl rollout undo
    end
    J->>K: smoke test via NodePort URL
```

## Components

| Layer | Tech | Responsibility |
|---|---|---|
| App | Flask 3 / Python 3.11 | REST endpoints; stateless except for `/client` SQLite write |
| Persistence | SQLite (file) | Demo persistence; mounted on `/data` volume |
| Container | Docker (multi-stage) | Reproducible runtime, non-root, healthcheck |
| Orchestration | Kubernetes | Replica management, rolling updates, autoscaling |
| CI primary | Jenkins | Full pipeline incl. Sonar gate, image push, deploy, rollback |
| CI secondary | GitHub Actions | Fast PR feedback, GHCR push on `main` |
| Quality | SonarQube + Postgres | Static analysis, coverage gating |
| Local IaC | Docker Compose | One-command spin-up of app + Sonar + Sonar DB |

## DevOps lifecycle mapping

| Phase | Tool(s) used in this project |
|---|---|
| Plan | GitHub Issues / branches |
| Code | Git, feature/bug branches |
| Build | Jenkins `Setup` + `Lint`, GitHub Actions `Build & Lint` |
| Test | pytest + pytest-cov (unit), `tests/integration/test_smoke.py` (integration) |
| Release | Jenkins `Docker Build` + `Docker Push` (immutable tags `:BUILD_NUMBER`) |
| Deploy | Jenkins `Deploy to Kubernetes` (`kubectl set image` rolling update) |
| Operate | Kubernetes Deployment + HPA + probes (self-healing, autoscaling) |
| Monitor | `/health` endpoint, `kubectl logs`, `kubectl get hpa` |

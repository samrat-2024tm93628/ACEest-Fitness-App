# Screenshot Checklist

Capture each item below and place under `docs/screenshots/` named exactly as
listed. Each item maps to a graded criterion in the assignment rubric.

> Tip: take screenshots at 1080p+; crop tight; include the relevant CLI/UI
> chrome (terminal title or browser address bar) so the grader can verify
> authenticity.

## 1. Source control / branching
| # | File name | What to capture |
|---|---|---|
| 1.1 | `01-git-log.png` | `git log --oneline --graph --all -15` showing branch/tag history |
| 1.2 | `02-github-repo.png` | GitHub repo page, branches dropdown visible |

## 2. Application running locally
| # | File name | What |
|---|---|---|
| 2.1 | `03-pytest-local.png` | `pytest` terminal output: `19 passed`, `coverage: 96%` |
| 2.2 | `04-curl-health.png` | `curl http://localhost:5000/health` JSON response |

## 3. Docker
| # | File name | What |
|---|---|---|
| 3.1 | `05-docker-build.png` | `docker build .` ending with `Successfully tagged aceest-fitness:latest` |
| 3.2 | `06-docker-images.png` | `docker images aceest-fitness` showing tags |
| 3.3 | `07-docker-compose-up.png` | `docker compose ps` — `app` + `sonarqube` + `sonar-db` healthy |

## 4. SonarQube
| # | File name | What |
|---|---|---|
| 4.1 | `08-sonar-scan-jenkins.png` | Jenkins console output of `SonarQube Analysis` stage |
| 4.2 | `09-sonar-dashboard.png` | SonarQube UI project page — coverage %, bugs, vulnerabilities |
| 4.3 | `10-sonar-quality-gate.png` | SonarQube Quality Gate "Passed" badge |

## 5. Jenkins pipeline
| # | File name | What |
|---|---|---|
| 5.1 | `11-jenkins-pipeline-overview.png` | Stage view showing all stages green |
| 5.2 | `12-jenkins-build-log.png` | Build log scrolled to a representative stage |
| 5.3 | `13-jenkins-test-results.png` | JUnit results panel (19 tests passed) |

## 6. GitHub Actions
| # | File name | What |
|---|---|---|
| 6.1 | `14-gh-actions-summary.png` | Workflow run summary, both jobs green |
| 6.2 | `15-ghcr-image.png` | Repo's `Packages` tab showing pushed image tag |

## 7. Kubernetes / Minikube
| # | File name | What |
|---|---|---|
| 7.1 | `16-minikube-status.png` | `minikube status` |
| 7.2 | `17-kubectl-apply.png` | `kubectl apply -f k8s/` output |
| 7.3 | `18-kubectl-get-pods.png` | `kubectl get pods -n aceest -o wide` showing 3 Running |
| 7.4 | `19-rollout-status.png` | `kubectl rollout status deployment/aceest -n aceest` "successfully rolled out" |
| 7.5 | `20-curl-via-nodeport.png` | Browser/curl hitting `minikube service aceest-nodeport`-resolved URL `/health` |

## 8. Rolling update + rollback
| # | File name | What |
|---|---|---|
| 8.1 | `21-set-image-v2.png` | `kubectl set image …:v2` followed by rolling pods |
| 8.2 | `22-rollout-history.png` | `kubectl rollout history deployment/aceest -n aceest` (≥2 revisions) |
| 8.3 | `23-rollout-undo.png` | `./scripts/rollback.sh` — undo + status output |

## 9. Autoscaling
| # | File name | What |
|---|---|---|
| 9.1 | `24-hpa-idle.png` | `kubectl get hpa -n aceest` at rest (replicas = 2) |
| 9.2 | `25-hpa-under-load.png` | Same command after generating load — replicas scaled to 4–6 |

## 10. (Optional bonus) Smoke tests against live cluster
| # | File name | What |
|---|---|---|
| 10.1 | `26-smoke-test.png` | `./scripts/smoke-test.sh` — 3 smoke tests passed |

## Capture order recommendation

Run this once, top to bottom, capturing as you go:

```bash
# 1-2 source/local
git log --oneline --graph --all -15
pytest

# 3 docker
docker build -t aceest-fitness:latest .
docker images aceest-fitness
docker compose up -d && docker compose ps

# 4 sonar (UI in browser)

# 5-6 CI (Jenkins UI + GitHub UI)

# 7-9 kubernetes
minikube start --driver=docker
eval $(minikube docker-env)
docker build -t aceest-fitness:latest .
./scripts/deploy.sh
kubectl get pods -n aceest -o wide
kubectl rollout status deployment/aceest -n aceest
minikube service aceest-nodeport -n aceest --url
docker build -t aceest-fitness:v2 .
./scripts/deploy.sh v2
kubectl rollout history deployment/aceest -n aceest
./scripts/rollback.sh

# 9 hpa
kubectl get hpa -n aceest
# in second terminal: load generator (see deployment-strategies demo)

# 10 smoke
./scripts/smoke-test.sh
```

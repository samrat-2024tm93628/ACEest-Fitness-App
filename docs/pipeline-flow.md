# CI/CD Pipeline Flow

The Jenkins pipeline ([Jenkinsfile](../Jenkinsfile)) is the authoritative
build-test-deploy path. GitHub Actions ([main.yml](../.github/workflows/main.yml))
runs in parallel on every push to give fast PR feedback and publishes the
image to GHCR on `main`.

## Jenkins pipeline

```mermaid
flowchart TD
    A[Checkout SCM] --> B[Setup venv<br/>install requirements-dev.txt]
    B --> C[Lint<br/>python -m compileall]
    C --> D[Test + Coverage<br/>pytest --cov, JUnit XML]
    D --> E{SONAR_ENABLED?}
    E -- yes --> F[SonarQube Analysis<br/>sonar-scanner]
    F --> G[Quality Gate<br/>waitForQualityGate abortPipeline:true]
    E -- no --> H[Docker Build<br/>tag :BUILD_NUMBER + :latest]
    G --> H
    H --> I{branch == main<br/>and DOCKER_REGISTRY set?}
    I -- yes --> J[Docker Push]
    I -- no --> K
    J --> K{branch == main<br/>and k8s/ exists?}
    K -- yes --> L[Deploy to K8s<br/>kubectl set image + rollout status]
    K -- no --> M
    L --> M{SMOKE_BASE_URL set?}
    M -- yes --> N[Smoke Test<br/>pytest -m smoke against live URL]
    M -- no --> Z[done]
    N --> Z

    L -. on rollout failure .-> R[post.failure:<br/>kubectl rollout undo]
```

### Stage purposes

| Stage | Why it exists | Failure mode |
|---|---|---|
| Checkout | reproducible source | aborts build |
| Setup | isolated venv from pinned deps | aborts build |
| Lint | catches syntax errors before tests | aborts build |
| Test + Coverage | functional correctness + Sonar input | aborts build, JUnit/coverage archived |
| SonarQube Analysis | static analysis upload | aborts build |
| Quality Gate | enforce coverage/bug thresholds | aborts build (`abortPipeline:true`) |
| Docker Build | immutable artifact, tagged `:BUILD_NUMBER` | aborts build |
| Docker Push | distribute artifact | aborts build |
| Deploy to K8s | apply rolling update | aborts build, triggers rollback |
| Smoke Test | proves the **deployed** code answers traffic | aborts build, triggers rollback |
| post.failure | automatic `kubectl rollout undo` | best-effort |

## GitHub Actions pipeline (parallel safety net)

```mermaid
flowchart LR
    P[push / PR] --> T[test job<br/>pytest --cov, upload XML artifacts]
    T --> D{branch == main?}
    D -- yes --> B[docker job<br/>buildx + push to ghcr.io]
    D -- no --> Z[done]
    B --> Z
```

GHCR-published images use these tags:
- `ghcr.io/<owner>/aceest-fitness:<commit-sha>`
- `ghcr.io/<owner>/aceest-fitness:latest`

## Quality gates summary

| Gate | Tool | Threshold | Blocks merge / deploy? |
|---|---|---|---|
| Lint | `compileall` | 0 syntax errors | yes |
| Unit tests | pytest | all pass | yes |
| Coverage | pytest-cov | currently 96% (target ≥ 60%) | yes (via Sonar) |
| Static analysis | SonarQube | bugs = 0, vulns = 0, gate = passed | yes (`abortPipeline:true`) |
| Smoke tests | pytest `-m smoke` | all pass against deployed URL | yes (triggers auto-rollback) |

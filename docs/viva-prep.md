# Viva Preparation

Concise, defensible answers tied to actual files in this repo. Pull up the
referenced file when answering — graders reward "show me where" responses.

## Pipeline & CI/CD

**Q: Walk me through your CI/CD pipeline.**
A: Jenkins is primary. Stages in [Jenkinsfile](../Jenkinsfile): Checkout →
Setup venv → Lint → Test+Coverage → SonarQube → Quality Gate → Docker Build →
Docker Push → Deploy to K8s → Smoke Test, with `post.failure` running
`kubectl rollout undo`. GitHub Actions runs in parallel for fast PR feedback
and pushes to GHCR on `main`.

**Q: Why two CI systems?**
A: GitHub Actions is free per-commit feedback that runs on every push and
catches problems before code review. Jenkins owns the production path
because it integrates with SonarQube (`withSonarQubeEnv` + `waitForQualityGate`)
and runs `kubectl` against my cluster. Splitting concerns keeps PR-loop fast
without sacrificing the full quality gate.

**Q: What is a quality gate?**
A: A SonarQube-enforced threshold (coverage %, new bugs = 0, vulnerabilities = 0)
that blocks the pipeline when violated. In Jenkins this is the
`waitForQualityGate abortPipeline: true` step — if Sonar marks the gate as
"Failed", the build fails and nothing deploys.

## Containers

**Q: Why a multi-stage Dockerfile?**
A: Stage 1 installs build deps into a prefix; stage 2 copies just that prefix
into a clean `python:3.11-slim`. The runtime image has no pip cache, no
compilers, no apt history — smaller image, smaller attack surface.

**Q: Why run as non-root?**
A: A container compromise that breaks out of the app shouldn't get root on
the host. [Dockerfile](../Dockerfile) creates user `ace` (uid 1001);
[k8s/deployment.yaml](../k8s/deployment.yaml) enforces `runAsNonRoot: true`
at the pod level so a misconfigured image can't accidentally run as root.

**Q: What does `readOnlyRootFilesystem: true` cost you?**
A: Anything that writes to disk needs an explicit volume. We mount
`emptyDir` on `/data` for the SQLite file; everything else is read-only.

## Kubernetes

**Q: Liveness vs readiness probe?**
A: Liveness restarts the container if it crashes/hangs. Readiness controls
whether the Service routes traffic to the pod. Both use `/health` here, but
their failure semantics are different: liveness failure = `kubectl restart`,
readiness failure = removed from endpoints (no restart).

**Q: How does HPA decide to scale?**
A: It reads metrics from `metrics-server` and compares against
`targetAverageUtilization: 70`. Critical detail: HPA only works if the
pod has `resources.requests.cpu` set, because utilization is calculated as
`actual / requested`. See [k8s/deployment.yaml](../k8s/deployment.yaml).

**Q: Why `maxUnavailable: 0`?**
A: It's the zero-downtime guarantee. Default `25%` would let one of three
pods go down during a rollout. With `maxUnavailable: 0` plus `maxSurge: 1`,
a new pod must come up and become ready before any old pod is removed, so
total ready replicas never dips below desired count.

**Q: Show me your rollback.**
A: Two layers. (1) Image-level: every Jenkins build produces an immutable
tag `:BUILD_NUMBER`, so I can deploy any historical version. (2) K8s-level:
`kubectl rollout undo deployment/aceest -n aceest` reverts the Deployment to
the previous ReplicaSet — wired into [Jenkinsfile](../Jenkinsfile)'s
`post.failure`. [scripts/rollback.sh](../scripts/rollback.sh) demonstrates
both interactive and revision-targeted rollback.

## Deployment strategies

**Q: Difference between rolling and blue/green?**
A: Rolling replaces pods incrementally; resource overhead is +1 surge replica.
Blue/green runs both versions in full at the same time and switches the
Service selector to cut over; resource overhead is 2× replicas during
cutover but rollback is instant (flip the selector back). Rolling has
overlapping versions in production briefly — schemas must be backward
compatible. See [docs/deployment-strategies.md](./deployment-strategies.md).

**Q: Canary?**
A: Two Deployments behind one Service, one with very few replicas. Traffic
splits roughly by replica ratio. Used to expose 1% of users to a new version
before promoting. Production-grade canary needs Ingress/mesh weighted
routing — out of scope here.

## Quality / testing

**Q: What's your coverage and how is it enforced?**
A: 96%, configured in [pytest.ini](../pytest.ini) which emits `coverage.xml`
on every test run. SonarQube reads it (see
[sonar-project.properties](../sonar-project.properties)) and gates on it.

**Q: Why the smoke tests?**
A: Unit tests prove the code is correct; smoke tests
([tests/integration/test_smoke.py](../tests/integration/test_smoke.py))
prove the **deployed** code answers traffic. They run against the live URL
after `rollout status` in the Jenkins `Smoke Test` stage. If they fail, the
post-failure handler rolls back automatically.

## Security & secrets

**Q: How do you handle secrets?**
A: `.env` is git-ignored; `.env.example` documents the contract. In
Kubernetes, [k8s/secret.yaml](../k8s/secret.yaml) defines an Opaque Secret
mounted via `envFrom` so the app reads `os.environ.get()` without knowing
the source. In Jenkins, `withCredentials([usernamePassword(...)])` injects
DockerHub creds without leaking them in the build log.

**Q: Why is the Secret in git?**
A: It's a placeholder for screenshots only — the comment at the top says so
and instructs the real-world flow:
`kubectl create secret generic aceest-secrets --from-env-file=.env -n aceest`
(don't commit the populated manifest).

## Infrastructure as Code

**Q: Where is your IaC?**
A: Two layers. (1) Kubernetes manifests in [k8s/](../k8s/) are themselves
declarative IaC — `kubectl apply -f k8s/` reproduces the entire app state.
(2) [docker-compose.yml](../docker-compose.yml) declares the local dev
stack (app + Sonar + Postgres). For cloud-level provisioning (cluster, VPC,
node pool) Terraform is the standard tool — covered conceptually in the
report.

## DevOps lifecycle

**Q: Map each lifecycle phase to a tool you're using.**
See the table at the bottom of [docs/architecture.md](./architecture.md).
Plan→GitHub, Code→Git, Build→Jenkins+GHA, Test→pytest, Release→Docker registry,
Deploy→`kubectl`, Operate→K8s probes/HPA, Monitor→`/health` + `kubectl logs`.

## Likely "trick" questions

**Q: What happens if Sonar is down when Jenkins runs?**
A: `waitForQualityGate` times out after 5 minutes (`timeout(time: 5, unit: 'MINUTES')`)
and fails the build. The `SONAR_ENABLED` env flag also lets us skip the
stage entirely on a Jenkins instance without Sonar configured.

**Q: What if `kubectl set image` succeeds but the new pods crash-loop?**
A: `kubectl rollout status` will time out after 2 minutes and the stage
fails. `post.failure` runs `kubectl rollout undo`, restoring the previous
ReplicaSet. The Deployment's `revisionHistoryLimit: 5` keeps the last 5
revisions available for rollback.

**Q: Your DB is SQLite — how does that work with multiple replicas?**
A: It doesn't, and that's intentional. SQLite is per-pod via `emptyDir` —
each pod has its own. For multi-replica persistence you'd swap `emptyDir`
for a `PersistentVolumeClaim` and use a real database (Postgres). This is
called out in [k8s/deployment.yaml](../k8s/deployment.yaml) comments.

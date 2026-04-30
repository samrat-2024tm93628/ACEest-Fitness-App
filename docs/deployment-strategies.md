# Deployment Strategies

This project **implements** rolling updates (the Kubernetes default) and
**demonstrates** blue/green at small scale. Canary, A/B, and shadow are
documented conceptually with concrete commands you could run on the same
cluster — they are not part of the default pipeline because they require
either a service mesh or non-trivial routing rules that exceed the assignment
scope.

## Comparison

| Strategy | Downtime | Risk | Resource overhead | Rollback speed | Implemented here |
|---|---|---|---|---|---|
| Recreate | Yes (full) | High | None (one version at a time) | Slow (re-deploy old) | No |
| **Rolling** | None (with `maxUnavailable: 0`) | Low | +1 replica during update | Fast (`rollout undo`) | **Yes (default)** |
| Blue/Green | None | Low (instant cutover) | 2× replicas during cutover | Instant (flip Service selector) | Yes (manual demo) |
| Canary | None | Lowest (% traffic) | +1 replica per canary | Fast (delete canary) | Concept |
| A/B | None | Lowest (header-routed) | +1 replica per variant | Fast | Concept (needs Ingress/mesh) |
| Shadow | None | Zero (no user impact) | Full mirror infra | N/A | Concept (needs mesh) |

## Rolling update — implemented

[k8s/deployment.yaml](../k8s/deployment.yaml) configures:

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0   # never drop below desired replica count
```

Combined with `readinessProbe` on `/health`, this gives **zero-downtime**
deploys: a new pod is added, becomes ready, then an old pod is terminated;
traffic is only routed to ready pods.

### Demo

```bash
./scripts/deploy.sh v1
# build a new image
docker build -t aceest-fitness:v2 .
./scripts/deploy.sh v2
kubectl rollout history deployment/aceest -n aceest
# kubectl rollout undo deployment/aceest -n aceest   # rollback
```

## Blue/Green — small demo

Run two Deployments (`aceest-blue`, `aceest-green`) with identical labels
except a `version` label. The Service selects on `version: blue`. To cut over,
patch the Service selector to `green`:

```bash
kubectl patch svc aceest -n aceest -p '{"spec":{"selector":{"version":"green"}}}'
```

Pros: instant cutover, instant rollback by patching the selector back.
Cons: 2× replicas during cutover; database schemas must be backwards-compatible.

## Canary — concept + commands

Run two Deployments behind one Service:
- `aceest` (stable, replicas=9)
- `aceest-canary` (replicas=1, `image: ...:vNEW`)

Both share a `app.kubernetes.io/name: aceest-fitness` label, so the Service
sends ~10% of traffic to the canary. Increase canary replicas to ramp up
exposure; delete the canary Deployment to roll back.

Production-grade canary needs traffic-percentage routing, which requires an
Ingress controller with weighted backends or a service mesh (Istio, Linkerd).

## A/B testing — concept

Same topology as canary, but routing decision is based on a request header
(e.g. `X-Variant: B`) rather than a percentage. Used to test product hypotheses,
not deployment safety. Requires Ingress/mesh.

## Shadow / dark traffic — concept

Production traffic is **mirrored** to a shadow Deployment. Responses from the
shadow are discarded. Used to load-test a new version against real traffic
without user impact. Requires service mesh `mirror` policy
(e.g. Istio `VirtualService.spec.http[].mirror`).

## Picking a strategy for ACEest

For an academic submission, **rolling update + automatic `rollout undo` on
failure** (already wired in [Jenkinsfile](../Jenkinsfile) `post.failure`) is
the right baseline. Blue/green is shown for completeness; canary/A-B/shadow
are covered as concepts in the report and viva.

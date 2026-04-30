#!/usr/bin/env bash
# Roll the deployment back to the previous ReplicaSet.
# Pass a specific revision number to roll back to that revision instead.
#   ./scripts/rollback.sh         # previous revision
#   ./scripts/rollback.sh 4       # revision 4 from `kubectl rollout history`
set -euo pipefail

NAMESPACE="${NAMESPACE:-aceest}"
DEPLOYMENT="${DEPLOYMENT:-aceest}"
REVISION="${1:-}"

echo ">> Rollout history:"
kubectl rollout history "deployment/${DEPLOYMENT}" -n "${NAMESPACE}"

if [[ -n "${REVISION}" ]]; then
  echo ">> Rolling back to revision ${REVISION}"
  kubectl rollout undo "deployment/${DEPLOYMENT}" --to-revision="${REVISION}" -n "${NAMESPACE}"
else
  echo ">> Rolling back to previous revision"
  kubectl rollout undo "deployment/${DEPLOYMENT}" -n "${NAMESPACE}"
fi

kubectl rollout status "deployment/${DEPLOYMENT}" -n "${NAMESPACE}" --timeout=2m
kubectl get pods -n "${NAMESPACE}"

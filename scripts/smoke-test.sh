#!/usr/bin/env bash
# Run integration smoke tests against the running deployment.
# Auto-detects Minikube service URL if not provided.
#   ./scripts/smoke-test.sh
#   BASE_URL=http://example.com ./scripts/smoke-test.sh
set -euo pipefail

NAMESPACE="${NAMESPACE:-aceest}"

if [[ -z "${BASE_URL:-}" ]]; then
  if command -v minikube >/dev/null 2>&1; then
    echo ">> Resolving service URL via minikube"
    BASE_URL="$(minikube service aceest-nodeport -n "${NAMESPACE}" --url | head -n1)"
  else
    echo "BASE_URL not set and minikube not found. Set BASE_URL explicitly."
    exit 1
  fi
fi

echo ">> Smoke testing ${BASE_URL}"
BASE_URL="${BASE_URL}" pytest -m smoke --no-cov -v

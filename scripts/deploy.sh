#!/usr/bin/env bash
# Deploy ACEest Fitness to the cluster currently in your kubectl context.
# Usage:
#   ./scripts/deploy.sh                 # uses image aceest-fitness:latest
#   ./scripts/deploy.sh v1.2.3          # uses aceest-fitness:v1.2.3
#   IMAGE=ghcr.io/me/aceest:abc ./scripts/deploy.sh
set -euo pipefail

NAMESPACE="${NAMESPACE:-aceest}"
DEPLOYMENT="${DEPLOYMENT:-aceest}"
TAG="${1:-latest}"
IMAGE="${IMAGE:-aceest-fitness:${TAG}}"

echo ">> Applying base manifests to namespace ${NAMESPACE}"
kubectl apply -f k8s/

echo ">> Setting image: ${IMAGE}"
kubectl set image "deployment/${DEPLOYMENT}" "app=${IMAGE}" -n "${NAMESPACE}" --record

echo ">> Waiting for rollout"
kubectl rollout status "deployment/${DEPLOYMENT}" -n "${NAMESPACE}" --timeout=2m

echo ">> Pods:"
kubectl get pods -n "${NAMESPACE}" -o wide

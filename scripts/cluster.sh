#!/usr/bin/env bash
# The local Kubernetes cluster (kind = Kubernetes in Docker).
#   scripts/cluster.sh up      create it (~1 minute)
#   scripts/cluster.sh pods    the game's copies, and their machines
#   scripts/cluster.sh down    delete it
set -euo pipefail
cd "$(dirname "$0")/.."
CLUSTER="${CLUSTER:-devops-example}"
case "${1:-}" in
  up)
    kind get clusters 2>/dev/null | grep -qx "$CLUSTER" || kind create cluster --config k8s/kind-cluster.yaml
    kubectl --context "kind-$CLUSTER" get nodes ;;
  pods) kubectl --context "kind-$CLUSTER" get pods -l app=game -o wide ;;
  down) kind delete cluster --name "$CLUSTER" ;;
  *) sed -n '2,5p' "$0" | sed 's/^# \{0,1\}//'; exit 1 ;;
esac

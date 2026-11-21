#!/usr/bin/env bash
# Deploy one image to the cluster: the files in k8s/, with this image. A rolling update.
#   scripts/deploy.sh game-site:v2
set -euo pipefail
cd "$(dirname "$0")/.."
TAG="${1:?usage: scripts/deploy.sh <image>}"
CLUSTER="${CLUSTER:-devops-example}"

# upload: copy the image onto every machine of the cluster
kind load docker-image "$TAG" --name "$CLUSTER" >/dev/null 2>&1
echo "   uploaded $TAG to the cluster's machines"

# the file is the truth - with the new image filled in
sed "s|^\( *image:\) [^ ]*|\1 $TAG|" k8s/deployment.yaml | kubectl --context "kind-$CLUSTER" apply -f -
kubectl --context "kind-$CLUSTER" apply -f k8s/service.yaml

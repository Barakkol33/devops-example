#!/usr/bin/env bash
# The pipeline - the same five steps on your laptop and in GitHub Actions:
#   1. BUILD     pack the code into an image
#   2. TEST      the unit tests (pytest), then a smoke test of the new image
#   3. DEPLOY    upload it, then a rolling update - one copy at a time
#   4. VERIFY    is every new copy ready? does the game answer with the new version?
#   5. ROLLBACK  only if 4 failed - back to the version that worked
#
#   scripts/pipeline.sh          (needs a cluster: scripts/cluster.sh up)
set -euo pipefail
cd "$(dirname "$0")/.."
CLUSTER="${CLUSTER:-devops-example}"
IMAGE="${IMAGE:-game-site}"          # in GitHub Actions: ghcr.io/<owner>/devops-example
URL="${URL:-http://localhost:8085}"   # in the talk demo: http://localhost:8080
k() { kubectl --context "kind-$CLUSTER" "$@"; }
stage() { printf '\n== %s\n' "$*"; }

read -r VERSION COLOR <VERSION
TAG="$IMAGE:$VERSION"
echo "PIPELINE - commit $(git log -1 --format='%h "%s"' 2>/dev/null || echo '(no git)') -> $TAG"

stage "1. BUILD - pack the code into an image"
docker build -q -t "$TAG" --build-arg VERSION="$VERSION" --build-arg COLOR="$COLOR" . >/dev/null
echo "   ok: built $TAG"

stage "2. TEST - the unit tests, then a smoke test of the new image"
docker build -q -t "$IMAGE-test:$VERSION" --target test . >/dev/null
if ! docker run --rm "$IMAGE-test:$VERSION" || ! { echo "   smoke test: the image starts and serves the game"; tests/smoke.sh "$TAG"; }; then
  echo "   FAILED: a test failed - nothing was deployed"
  exit 1
fi
echo "   ok: all tests passed"

stage "3. DEPLOY - upload the image, then a rolling update, one copy at a time"
first=0
k get deployment/game >/dev/null 2>&1 || first=1
scripts/deploy.sh "$TAG"

stage "4. VERIFY - is every new copy ready, and does the game answer with $VERSION?"
verified=0
if k rollout status deployment/game --timeout=60s; then
  for _ in $(seq 1 30); do
    answer=$(curl -s --max-time 1 "$URL/plain" || true)
    if [[ "$answer" == "$VERSION "* ]]; then verified=1; break; fi
    sleep 1
  done
  (( verified )) || echo "   FAILED: the game does not answer with $VERSION"
else
  echo "   FAILED: the new copies never became ready"
fi
if (( verified )); then
  echo "   ok: $VERSION is live: $answer"
  echo
  echo "PIPELINE PASSED - $VERSION released"
  exit 0
fi

stage "5. ROLLBACK - automatic"
if (( first )); then
  echo "   nothing to roll back to - this was the first deploy"
else
  k rollout undo deployment/game
  k rollout status deployment/game --timeout=60s
  echo "   back to: $(curl -s --max-time 1 "$URL/plain")"
fi
echo
echo "PIPELINE FAILED - players kept the last version that worked"
exit 1

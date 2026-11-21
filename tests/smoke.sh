#!/bin/sh
# Smoke test: start the real image, and check that the game answers - before it goes anywhere.
#   tests/smoke.sh game-site:v2
img="$1"
cid=$(docker run -d --rm "$img") || exit 1
ok=1
for _ in $(seq 1 20); do
  if docker exec "$cid" python -c "import urllib.request as u; assert b'<title>4096</title>' in u.urlopen('http://127.0.0.1:8000/').read()" 2>/dev/null; then
    ok=0; break
  fi
  sleep 0.5
done
docker stop "$cid" >/dev/null
exit $ok

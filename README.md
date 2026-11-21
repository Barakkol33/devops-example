# devops-example: 4096

**4096**, as a small Python web app - and the whole road it takes from code to many players:
**Git → Docker → CI/CD → Kubernetes**. Every step is real, and every step also runs on your own laptop.

It's the example for the talk [From Code to the Real World](https://barakkol33.github.io/blearning/tech/software-development/devops/talk/) on blearning.

| you want to... | the tool | here |
| --- | --- | --- |
| save every change, and be able to go back | **Git** | this repository - see its [history](../../commits/main) |
| pack it, so it runs the same anywhere | **Docker** | [Dockerfile](Dockerfile) |
| check every change, and ship it by itself | **CI/CD** | [scripts/pipeline.sh](scripts/pipeline.sh), run by [GitHub Actions](.github/workflows/pipeline.yml) on every push and pull request - see the [runs](../../actions) |
| run many copies, that heal themselves | **Kubernetes** | [k8s/](k8s/) - 3 copies behind one address |

## What's in it

The code - three files (the branch [`app-only`](../../tree/app-only) has just these):

```text
main.py                    the web server (FastAPI): the page, the game API, /healthz, /plain - run: python main.py
board.py                   the rules of 4096: slide, merge, score, game over - pure Python
static/index.html          the page: draws the board and sends your moves - the rules stay in Python
requirements.txt           what the game needs (FastAPI, uvicorn)
```

And everything around it - the tests, and the road to the players:

```text
tests/
  test_board.py            unit tests for the rules (pytest)
  test_app.py              tests for the web server
  smoke.sh                 the real image starts and serves the game
requirements-dev.txt       the test tools (pytest)
Dockerfile                 the image, in stages: base -> test (runs pytest) -> app (the game)
VERSION                    the version and its color: v1 blue, v2 green, v3 red
k8s/
  kind-cluster.yaml        a 3-machine Kubernetes cluster, inside Docker
  deployment.yaml          "always keep 3 copies of the game running"
  service.yaml             the load balancer: one address for every player
scripts/
  cluster.sh               start / stop the local cluster
  pipeline.sh              build -> test -> deploy -> verify -> rollback
  deploy.sh                deploy one image (the pipeline's step 3)
.github/workflows/pipeline.yml   the same pipeline, in GitHub Actions
```

**The server keeps nothing between moves.** The page sends the board with every move, and the server answers with the new board. So any copy of the server can answer any request - that's what lets Kubernetes run many copies behind one address, and replace one that dies, without anyone losing their game.

## Run it as a Python project

You need Python 3.11+.

```bash
python -m venv .venv && . .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python -m pytest                                 # the tests
python main.py                                   # the game: http://localhost:8000
```

## The pipeline

Every push to `main` and every pull request runs [the pipeline](.github/workflows/pipeline.yml) in GitHub Actions. GitHub starts a fresh Kubernetes cluster for the run, deploys the version that's live now (the last release), and then runs the same script you can run on your laptop:

1. **BUILD** - pack the code into an image.
2. **TEST** - the unit tests (pytest, inside the image's `test` stage), then a smoke test: the real image starts and serves the game.
3. **DEPLOY** - upload the image, then a **rolling update**: a new copy starts, and only when it's ready does an old one stop.
4. **VERIFY** - are all the new copies ready? Does the game answer with the new version?
5. **ROLLBACK** - only if step 4 failed: back to the version that worked, by itself.

On `main`, a version that passed is **released**: its image is pushed to GitHub's registry, and the next run starts from it. Anyone can run a release: `docker run -p 8000:8000 ghcr.io/barakkol33/devops-example:v2`.

**The bug, as a pull request.** The branch [`bug/rename-healthz`](../../compare/main...bug/rename-healthz) is an AI "tidy-up": it renames the address `/healthz` to `/health` - and updates the test to match, so every test passes. But Kubernetes asks each copy `/healthz` ("are you ready?" - it's in [k8s/deployment.yaml](k8s/deployment.yaml)), so the new copies never become ready. VERIFY fails, the pipeline rolls back, and the pull request gets a red X. Open its pipeline run to see every step.

## Run the whole road on your laptop

You need Docker, [kind](https://kind.sigs.k8s.io/) and `kubectl` (on Windows: inside WSL). The [setup page on blearning](https://barakkol33.github.io/blearning/tech/software-development/devops/prerequisites/) walks through it.

```bash
scripts/cluster.sh up        # a 3-machine Kubernetes cluster, ~1 minute
scripts/pipeline.sh          # build, test, deploy the current version
scripts/cluster.sh pods      # 3 copies, on 2 machines
```

Open <http://localhost:8085> and play. The line at the bottom says which version, which copy and which machine answered.

**Ship a new level** - the same upgrade as in Git's history: start from v1, then roll out v2 (a bigger board: 5x5).

```bash
git switch --detach v1       # v1 - the first version
scripts/pipeline.sh          # -> PIPELINE PASSED - v1 released
git switch main              # v2 - "a bigger board" (git show v2 to see the change)
scripts/pipeline.sh          # -> a rolling update to v2, PIPELINE PASSED
```

**See self-healing:** kill a copy, and watch a new one start - nobody restarts it.

```bash
kubectl --context kind-devops-example delete pod -l app=game --wait=false
scripts/cluster.sh pods
```

**See the rollback:** `git switch bug/rename-healthz && scripts/pipeline.sh` - the tests pass, VERIFY fails, and it rolls back.

When you're done: `scripts/cluster.sh down`.

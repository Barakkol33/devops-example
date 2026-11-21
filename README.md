# devops-example: 4096

**4096**, as a small Python web app: the rules in Python, a thin page in the browser.

```bash
pip install -r requirements.txt
python main.py               # then open http://localhost:8000
```

| file | what it is |
| --- | --- |
| [main.py](main.py) | the web server (FastAPI): the page, and the game's API |
| [board.py](board.py) | the rules of 4096: slide, merge, score, game over - pure Python |
| [static/index.html](static/index.html) | the page: draws the board and sends your moves |
| [requirements.txt](requirements.txt) | the libraries the game needs |

This branch is only the code. [`main`](../../tree/main) adds the tests and the road to many players: Git, Docker, CI/CD and Kubernetes.

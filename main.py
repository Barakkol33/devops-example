"""The game's web server: the page, the game API, and two addresses for the system around it.

Run it:  python main.py   - then open http://localhost:8000

The server keeps nothing between requests: the page sends the board with every move.
So any copy of the server can answer any request - which is what lets Kubernetes run
many copies, and replace one that dies, without anyone losing their game.
"""
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel

import board as rules

app = FastAPI(title="2048")
PAGE = Path(__file__).parent / "static" / "index.html"


class Game(BaseModel):
    board: list[list[int]]
    score: int = 0


class Move(Game):
    direction: str


def game_state(board: rules.Board, score: int, moved: bool = True) -> dict:
    return {"board": board, "score": score, "moved": moved,
            "won": rules.has_won(board), "game_over": not rules.can_move(board)}


@app.get("/")
def page():
    return FileResponse(PAGE)


@app.post("/api/new")
def new_game():
    return game_state(rules.new_board(), 0)


@app.post("/api/move")
def make_move(request: Move):
    try:
        board, points, moved = rules.move(request.board, request.direction)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    if moved:
        board = rules.add_tile(board)
    return game_state(board, request.score + points, moved)


# Kubernetes asks this every second: "are you ready for players?"
@app.get("/health", response_class=PlainTextResponse)
def health():
    return "ok"


# which version, color, copy and machine answered - for the page's bottom line and for dashboards
@app.get("/plain", response_class=PlainTextResponse)
def plain():
    return " ".join(os.environ.get(name, default) for name, default in
                    [("VERSION", "dev"), ("COLOR", "#8250df"), ("POD_NAME", "my-laptop"), ("NODE_NAME", "my-laptop")])


if __name__ == "__main__":
    import uvicorn

    host = os.environ.get("HOST", "127.0.0.1")    # the container sets 0.0.0.0, to accept requests from outside it
    port = int(os.environ.get("PORT", "8000"))
    print(f"2048 is running - open http://localhost:{port}")
    uvicorn.run(app, host=host, port=port)

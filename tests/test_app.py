"""Tests for the web server (main.py), without starting a real server."""
from fastapi.testclient import TestClient

import board as rules
from main import app

client = TestClient(app)


def test_the_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "<title>2048</title>" in response.text


def test_new_game():
    game = client.post("/api/new").json()
    assert sum(1 for row in game["board"] for v in row if v) == rules.START_TILES
    assert game["score"] == 0 and not game["game_over"]


def test_a_move_merges_scores_and_adds_a_tile():
    game = client.post("/api/move", json={"board": [[2, 2], [0, 0]], "score": 10, "direction": "left"}).json()
    assert game["board"][0][0] == 4
    assert game["score"] == 14
    assert sum(1 for row in game["board"] for v in row if v) == 2     # the merged 4, plus a new tile


def test_a_bad_direction_is_rejected():
    response = client.post("/api/move", json={"board": [[2, 2], [0, 0]], "direction": "sideways"})
    assert response.status_code == 400


def test_health():
    assert client.get("/health").text == "ok"


def test_plain_says_which_version_answered():
    assert client.get("/plain").text.split()[0] == "dev"

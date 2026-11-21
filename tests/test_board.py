"""Tests for the rules of 4096 (board.py)."""
import random

import pytest

import board as rules


@pytest.mark.parametrize("row, expected, points", [
    ([2, 2, 0, 0], [4, 0, 0, 0], 4),        # two equal tiles merge
    ([0, 2, 0, 2], [4, 0, 0, 0], 4),        # gaps don't matter
    ([2, 2, 2, 2], [4, 4, 0, 0], 8),        # two separate merges
    ([4, 4, 8, 0], [8, 8, 0, 0], 8),        # a merged tile doesn't merge again in the same move
    ([2, 4, 8, 16], [2, 4, 8, 16], 0),      # nothing to merge, nothing moves
    ([0, 0, 0, 0], [0, 0, 0, 0], 0),
])
def test_slide_row_left(row, expected, points):
    assert rules.slide_row_left(row) == (expected, points)


def test_move_in_every_direction():
    board = [[2, 0, 0, 2],
             [0, 0, 0, 0],
             [0, 0, 0, 0],
             [2, 0, 0, 0]]
    assert rules.move(board, "left")[0][0] == [4, 0, 0, 0]
    assert rules.move(board, "right")[0][0] == [0, 0, 0, 4]
    assert rules.move(board, "up")[0][0] == [4, 0, 0, 2]
    assert rules.move(board, "down")[0][3] == [4, 0, 0, 2]


def test_move_reports_points_and_whether_anything_moved():
    board = [[2, 2], [0, 0]]
    assert rules.move(board, "left") == ([[4, 0], [0, 0]], 4, True)
    assert rules.move(board, "up") == ([[2, 2], [0, 0]], 0, False)


def test_unknown_direction():
    with pytest.raises(ValueError):
        rules.move(rules.empty_board(), "sideways")


def test_new_board_has_its_start_tiles():
    board = rules.new_board(rng=random.Random(1))
    tiles = [v for row in board for v in row if v]
    assert len(board) == rules.SIZE and len(tiles) == rules.START_TILES
    assert set(tiles) <= {2, 4}


def test_add_tile_fills_an_empty_cell_and_leaves_a_full_board_alone():
    board = [[2, 4], [8, 0]]
    assert rules.add_tile(board, random.Random(0))[1][1] in (2, 4)
    full = [[2, 4], [8, 16]]
    assert rules.add_tile(full) == full


def test_game_over_only_when_no_move_is_left():
    stuck = [[2, 4], [4, 2]]
    assert not rules.can_move(stuck)
    assert rules.can_move([[2, 2], [4, 8]])      # two equal neighbours
    assert rules.can_move([[2, 4], [8, 0]])      # an empty cell


def test_has_won():
    assert rules.has_won([[4096, 0], [0, 0]])
    assert not rules.has_won([[2048, 2048], [0, 0]])

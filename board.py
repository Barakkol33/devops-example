"""The rules of 4096 - pure Python, no web, no randomness you can't control.

A board is a list of rows; each row is a list of numbers, and 0 is an empty cell:

    [[2, 0, 0, 2],
     [0, 4, 0, 0],
     [0, 0, 0, 0],
     [0, 0, 2, 0]]

Slide the tiles left, right, up or down. Two equal tiles that touch merge into one,
and their sum is added to the score. After every move that changed the board,
a new tile (usually a 2, sometimes a 4) appears in a random empty cell.
"""
import random

SIZE = 4            # the board is SIZE x SIZE
START_TILES = 2     # how many tiles a new game starts with
WINNING_TILE = 4096
DIRECTIONS = ("left", "right", "up", "down")

Board = list[list[int]]


def empty_board(size: int = SIZE) -> Board:
    return [[0] * size for _ in range(size)]


def add_tile(board: Board, rng: random.Random = random) -> Board:
    """Put a 2 (90%) or a 4 (10%) in a random empty cell. A full board stays as it is."""
    empty = [(r, c) for r, row in enumerate(board) for c, value in enumerate(row) if value == 0]
    if not empty:
        return board
    r, c = rng.choice(empty)
    new = [row[:] for row in board]
    new[r][c] = 4 if rng.random() < 0.1 else 2
    return new


def new_board(size: int = SIZE, rng: random.Random = random) -> Board:
    """A new game: an empty board with START_TILES tiles."""
    board = empty_board(size)
    for _ in range(START_TILES):
        board = add_tile(board, rng)
    return board


def slide_row_left(row: list[int]) -> tuple[list[int], int]:
    """Slide one row to the left and merge equal neighbours - each tile merges at most once.

    Returns the new row and the points scored: [2, 2, 2, 2] -> ([4, 4, 0, 0], 8)
    """
    tiles = [value for value in row if value]
    merged, points, i = [], 0, 0
    while i < len(tiles):
        if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
            merged.append(tiles[i] * 2)
            points += tiles[i] * 2
            i += 2
        else:
            merged.append(tiles[i])
            i += 1
    return merged + [0] * (len(row) - len(merged)), points


def _transpose(board: Board) -> Board:
    return [list(column) for column in zip(*board)]


def _mirror(board: Board) -> Board:
    return [row[::-1] for row in board]


def move(board: Board, direction: str) -> tuple[Board, int, bool]:
    """Move every tile in one direction. Returns (new board, points scored, did anything move?).

    Every direction is "left" in disguise: turn the board, slide left, turn it back.
    """
    if direction not in DIRECTIONS:
        raise ValueError(f"unknown direction: {direction!r}")
    turned = board
    if direction in ("up", "down"):
        turned = _transpose(turned)
    if direction in ("right", "down"):
        turned = _mirror(turned)

    slid, points = [], 0
    for row in turned:
        new_row, row_points = slide_row_left(row)
        slid.append(new_row)
        points += row_points

    if direction in ("right", "down"):
        slid = _mirror(slid)
    if direction in ("up", "down"):
        slid = _transpose(slid)
    return slid, points, slid != board


def can_move(board: Board) -> bool:
    """Is there any move left? (an empty cell, or two equal neighbours)"""
    return any(move(board, direction)[2] for direction in DIRECTIONS)


def has_won(board: Board) -> bool:
    return any(value >= WINNING_TILE for row in board for value in row)

# chess-engine-project

A two-player chess game written in Python with [pygame](https://pyga.me/). You play both sides on one screen. The engine generates legal moves, including checks, pins and double checks.

There is no computer opponent yet. "Engine" here means the rules engine that works out which moves are legal.

## Features

- Legal move generation for all pieces
- Check, double check and pin detection: you can't make a move that leaves your king in check
- Undo moves with the left arrow key or `Z`
- Moves are printed to the terminal in coordinate notation (e.g. `e2e4`)
- Move generation is checked against standard [perft](https://www.chessprogramming.org/Perft_Results) counts from the starting position

### Not yet implemented

- Castling
- En passant
- Pawn promotion (a pawn that reaches the last rank stays a pawn and can't move)
- Checkmate and stalemate detection (the game doesn't announce the result; the side to move just has no legal moves)
- A computer opponent

## Getting started

You need Python 3.10 or newer. The easiest way to run it is with [uv](https://docs.astral.sh/uv/):

```bash
git clone https://github.com/VerheyeSil/chess-engine-project.git
cd chess-engine-project
uv run chess
```

Or with pip and a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -e .
chess                       # or: python -m chess_engine
```

## How to play

| Action | Control |
| --- | --- |
| Select a piece | Click its square |
| Move it | Click the target square |
| Deselect | Click the same square again |
| Undo last move | Left arrow or `Z` |

White moves first. Illegal moves are ignored.

## Project structure

```
chess-engine-project/
├── src/chess_engine/
│   ├── engine.py         # Game state, move generation, checks and pins
│   ├── gui.py            # Pygame window, drawing and mouse input
│   ├── __main__.py       # Entry point for `python -m chess_engine`
│   └── assets/images/    # Piece images (wP.png, bK.png, ...)
├── tests/
│   └── test_engine.py    # Perft and rules tests
└── pyproject.toml
```

The board is an 8x8 list of strings such as `"wP"` (white pawn) or `"bK"` (black king), with `"--"` for empty squares. Row 0 is black's back rank.

## Running the tests

```bash
uv run pytest
```

## Credits

This project is based on Eddie Sharick's "Chess Engine in Python" YouTube series. The original game and move generation code come from that series. The bug fixes, restructuring and tests were added on top of it, and new features are built from here.

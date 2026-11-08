"""Pygame front end: draws the board and turns mouse clicks into moves."""

from __future__ import annotations

from pathlib import Path

import pygame as p

from chess_engine.engine import EMPTY, GameState, Move

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGE_DIR = Path(__file__).parent / "assets" / "images"
PIECES = ["wP", "wR", "wN", "wB", "wQ", "wK", "bP", "bR", "bN", "bB", "bQ", "bK"]
LIGHT_SQUARE = p.Color("light gray")
DARK_SQUARE = p.Color("dark green")


def load_images() -> dict[str, p.Surface]:
    """Load and scale one image per piece, keyed by piece code (e.g. ``"wP"``)."""
    return {
        piece: p.transform.scale(p.image.load(IMAGE_DIR / f"{piece}.png"), (SQ_SIZE, SQ_SIZE))
        for piece in PIECES
    }


def draw_game_state(screen: p.Surface, gs: GameState, images: dict[str, p.Surface]) -> None:
    draw_board(screen)
    draw_pieces(screen, gs.board, images)


def draw_board(screen: p.Surface) -> None:
    """Draw the squares. The top-left square is always light."""
    colors = [LIGHT_SQUARE, DARK_SQUARE]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            p.draw.rect(screen, colors[(r + c) % 2], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen: p.Surface, board: list[list[str]], images: dict[str, p.Surface]) -> None:
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != EMPTY:
                screen.blit(images[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def main() -> None:
    """Open the window and run the game loop."""
    p.init()
    p.display.set_caption("Chess")
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    images = load_images()

    gs = GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False
    sq_selected: tuple[int, int] | tuple[()] = ()  # Last square the player clicked.
    player_clicks: list[tuple[int, int]] = []  # Up to two clicks: from and to.

    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:
                x, y = p.mouse.get_pos()
                row, col = y // SQ_SIZE, x // SQ_SIZE
                if sq_selected == (row, col):
                    # Clicking the same square twice deselects it.
                    sq_selected = ()
                    player_clicks = []
                else:
                    sq_selected = (row, col)
                    player_clicks.append(sq_selected)
                if len(player_clicks) == 2:
                    move = Move(player_clicks[0], player_clicks[1], gs.board)
                    if move in valid_moves:
                        print(move.get_chess_notation())
                        gs.make_move(move)
                        move_made = True
                        sq_selected = ()
                        player_clicks = []
                    else:
                        player_clicks = [sq_selected]

            elif e.type == p.KEYDOWN and e.key in (p.K_LEFT, p.K_z):
                gs.undo_move()
                move_made = True

        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False

        draw_game_state(screen, gs, images)
        clock.tick(MAX_FPS)
        p.display.flip()

    p.quit()


if __name__ == "__main__":
    main()

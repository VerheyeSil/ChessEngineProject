import pytest

from chess_engine.engine import EMPTY, GameState, Move


def perft(gs: GameState, depth: int) -> int:
    """Count every legal move sequence of the given length."""
    if depth == 0:
        return 1
    total = 0
    for move in gs.get_valid_moves():
        gs.make_move(move)
        total += perft(gs, depth - 1)
        gs.undo_move()
    return total


def empty_game(white_to_move: bool = True) -> GameState:
    gs = GameState()
    gs.board = [[EMPTY] * 8 for _ in range(8)]
    gs.white_to_move = white_to_move
    return gs


def place(gs: GameState, piece: str, square: str) -> None:
    row = Move.ranks_to_rows[square[1]]
    col = Move.files_to_cols[square[0]]
    gs.board[row][col] = piece
    if piece == "wK":
        gs.white_king_location = (row, col)
    elif piece == "bK":
        gs.black_king_location = (row, col)


def notations(moves: list[Move]) -> set[str]:
    return {m.get_chess_notation() for m in moves}


# Reference counts from the standard starting position. Castling, en passant
# and promotion can't happen within four plies, so these must match exactly.
@pytest.mark.parametrize(("depth", "expected"), [(1, 20), (2, 400), (3, 8902), (4, 197_281)])
def test_perft_from_start(depth: int, expected: int) -> None:
    assert perft(GameState(), depth) == expected


def test_make_and_undo_restore_position() -> None:
    gs = GameState()
    before = [row[:] for row in gs.board]
    gs.make_move(Move((6, 4), (4, 4), gs.board))
    assert gs.board[4][4] == "wP"
    assert not gs.white_to_move
    gs.undo_move()
    assert gs.board == before
    assert gs.white_to_move


def test_undo_with_empty_log_does_nothing() -> None:
    gs = GameState()
    gs.undo_move()
    assert gs.white_to_move


def test_pinned_knight_cannot_move() -> None:
    gs = empty_game()
    place(gs, "wK", "e1")
    place(gs, "wN", "e2")
    place(gs, "bR", "e8")
    place(gs, "bK", "a8")
    assert not any(m.piece_moved == "wN" for m in gs.get_valid_moves())


def test_black_pawn_pinned_on_diagonal_cannot_push() -> None:
    gs = empty_game(white_to_move=False)
    place(gs, "bK", "e8")
    place(gs, "bP", "f7")
    place(gs, "wB", "h5")
    place(gs, "wK", "a1")
    assert not any(m.piece_moved == "bP" for m in gs.get_valid_moves())


def test_black_pawn_can_capture_onto_h_file() -> None:
    gs = empty_game(white_to_move=False)
    place(gs, "bK", "a8")
    place(gs, "bP", "g5")
    place(gs, "wN", "h4")
    place(gs, "wK", "a1")
    assert "g5h4" in notations(gs.get_valid_moves())


def test_check_from_lower_left_diagonal_is_detected() -> None:
    gs = empty_game()
    place(gs, "wK", "e4")
    place(gs, "bB", "c2")
    place(gs, "bK", "h8")
    in_check, _, checks = gs.check_for_pins_and_checks()
    assert in_check
    assert len(checks) == 1


def test_must_respond_to_check() -> None:
    gs = empty_game()
    place(gs, "wK", "e1")
    place(gs, "wR", "a2")
    place(gs, "bR", "e8")
    place(gs, "bK", "h8")
    moves = notations(gs.get_valid_moves())
    assert "a2e2" in moves  # Block.
    assert "a2a3" not in moves  # Ignores the check.
    assert "e1e2" not in moves  # Still on the rook's file.


def test_notation() -> None:
    gs = GameState()
    assert Move((6, 4), (4, 4), gs.board).get_chess_notation() == "e2e4"

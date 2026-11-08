"""Chess rules: board state, move generation and move history.

The board is an 8x8 list of two-character strings. The first character is the
colour (``w`` or ``b``), the second the piece type (``P``, ``R``, ``N``, ``B``,
``Q``, ``K``). Empty squares are ``"--"``. Row 0 is black's back rank (rank 8)
and column 0 is the a-file.
"""

from __future__ import annotations

EMPTY = "--"

ROOK_DIRECTIONS = ((-1, 0), (0, -1), (1, 0), (0, 1))
BISHOP_DIRECTIONS = ((-1, 1), (-1, -1), (1, 1), (1, -1))
KNIGHT_OFFSETS = ((2, -1), (2, 1), (-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2))
KING_OFFSETS = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))


def on_board(row: int, col: int) -> bool:
    return 0 <= row < 8 and 0 <= col < 8


class GameState:
    """The current position, whose turn it is, and the list of moves played."""

    def __init__(self) -> None:
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.move_functions = {
            "P": self.get_pawn_moves,
            "R": self.get_rook_moves,
            "N": self.get_knight_moves,
            "B": self.get_bishop_moves,
            "Q": self.get_queen_moves,
            "K": self.get_king_moves,
        }
        self.move_log: list[Move] = []
        self.white_to_move = True
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.in_check = False
        self.pins: list[tuple[int, int, int, int]] = []
        self.checks: list[tuple[int, int, int, int]] = []

    def make_move(self, move: Move) -> None:
        """Play a move. Castling, promotion and en passant are not supported yet."""
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.board[move.start_row][move.start_col] = EMPTY
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_col)

    def undo_move(self) -> None:
        """Take back the last move, if there is one."""
        if not self.move_log:
            return
        move = self.move_log.pop()
        self.board[move.start_row][move.start_col] = move.piece_moved
        self.board[move.end_row][move.end_col] = move.piece_captured
        self.white_to_move = not self.white_to_move
        if move.piece_moved == "wK":
            self.white_king_location = (move.start_row, move.start_col)
        elif move.piece_moved == "bK":
            self.black_king_location = (move.start_row, move.start_col)

    def get_valid_moves(self) -> list[Move]:
        """All legal moves for the side to move, taking checks and pins into account."""
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()
        if self.white_to_move:
            king_row, king_col = self.white_king_location
        else:
            king_row, king_col = self.black_king_location

        if not self.in_check:
            return self.get_all_possible_moves()

        if len(self.checks) > 1:
            # Double check: only the king can move.
            moves: list[Move] = []
            self.get_king_moves(king_row, king_col, moves)
            return moves

        # Single check: capture the checker, block it, or move the king.
        moves = self.get_all_possible_moves()
        check_row, check_col, dir_row, dir_col = self.checks[0]
        piece_checking = self.board[check_row][check_col]
        if piece_checking[1] == "N":
            # A knight check can't be blocked.
            valid_squares = [(check_row, check_col)]
        else:
            valid_squares = []
            for i in range(1, 8):
                square = (king_row + dir_row * i, king_col + dir_col * i)
                valid_squares.append(square)
                if square == (check_row, check_col):
                    break
        return [
            m for m in moves
            if m.piece_moved[1] == "K" or (m.end_row, m.end_col) in valid_squares
        ]

    def get_all_possible_moves(self) -> list[Move]:
        """All moves for the side to move, without checking whether the king is left in check."""
        moves: list[Move] = []
        colour = "w" if self.white_to_move else "b"
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece[0] == colour:
                    self.move_functions[piece[1]](r, c, moves)
        return moves

    def _pin_for(self, r: int, c: int, remove: bool) -> tuple[bool, tuple[int, int] | tuple[()]]:
        """Return whether the piece on (r, c) is pinned and along which direction."""
        for i in range(len(self.pins) - 1, -1, -1):
            pin = self.pins[i]
            if pin[0] == r and pin[1] == c:
                if remove:
                    self.pins.remove(pin)
                return True, (pin[2], pin[3])
        return False, ()

    def get_pawn_moves(self, r: int, c: int, moves: list[Move]) -> None:
        pinned, pin_direction = self._pin_for(r, c, remove=False)
        if self.white_to_move:
            step, start_row, enemy = -1, 6, "b"
        else:
            step, start_row, enemy = 1, 1, "w"

        end_row = r + step
        if not 0 <= end_row < 8:
            # Pawn on the last rank. Promotion isn't implemented yet.
            return

        if self.board[end_row][c] == EMPTY and (not pinned or pin_direction == (step, 0)):
            moves.append(Move((r, c), (end_row, c), self.board))
            if r == start_row and self.board[r + 2 * step][c] == EMPTY:
                moves.append(Move((r, c), (r + 2 * step, c), self.board))

        for dc in (-1, 1):
            end_col = c + dc
            if 0 <= end_col < 8 and self.board[end_row][end_col][0] == enemy:
                if not pinned or pin_direction == (step, dc):
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def _get_sliding_moves(self, r, c, moves, directions, pinned, pin_direction) -> None:
        enemy = "b" if self.white_to_move else "w"
        for d in directions:
            if pinned and pin_direction not in (d, (-d[0], -d[1])):
                continue
            for i in range(1, 8):
                end_row, end_col = r + d[0] * i, c + d[1] * i
                if not on_board(end_row, end_col):
                    break
                end_piece = self.board[end_row][end_col]
                if end_piece == EMPTY:
                    moves.append(Move((r, c), (end_row, end_col), self.board))
                elif end_piece[0] == enemy:
                    moves.append(Move((r, c), (end_row, end_col), self.board))
                    break
                else:
                    break

    def get_rook_moves(self, r: int, c: int, moves: list[Move]) -> None:
        # A queen's pin is kept so get_bishop_moves can still see it.
        is_queen = self.board[r][c][1] == "Q"
        pinned, pin_direction = self._pin_for(r, c, remove=not is_queen)
        self._get_sliding_moves(r, c, moves, ROOK_DIRECTIONS, pinned, pin_direction)

    def get_bishop_moves(self, r: int, c: int, moves: list[Move]) -> None:
        pinned, pin_direction = self._pin_for(r, c, remove=True)
        self._get_sliding_moves(r, c, moves, BISHOP_DIRECTIONS, pinned, pin_direction)

    def get_knight_moves(self, r: int, c: int, moves: list[Move]) -> None:
        pinned, _ = self._pin_for(r, c, remove=True)
        if pinned:
            # A pinned knight can never move.
            return
        ally = "w" if self.white_to_move else "b"
        for dr, dc in KNIGHT_OFFSETS:
            end_row, end_col = r + dr, c + dc
            if on_board(end_row, end_col) and self.board[end_row][end_col][0] != ally:
                moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_queen_moves(self, r: int, c: int, moves: list[Move]) -> None:
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_king_moves(self, r: int, c: int, moves: list[Move]) -> None:
        ally = "w" if self.white_to_move else "b"
        for dr, dc in KING_OFFSETS:
            end_row, end_col = r + dr, c + dc
            if not on_board(end_row, end_col) or self.board[end_row][end_col][0] == ally:
                continue
            # Put the king on the target square temporarily and see if it would be in check.
            if ally == "w":
                self.white_king_location = (end_row, end_col)
            else:
                self.black_king_location = (end_row, end_col)
            in_check, _, _ = self.check_for_pins_and_checks()
            if not in_check:
                moves.append(Move((r, c), (end_row, end_col), self.board))
            if ally == "w":
                self.white_king_location = (r, c)
            else:
                self.black_king_location = (r, c)

    def check_for_pins_and_checks(self):
        """Look outward from the side-to-move's king.

        Returns ``(in_check, pins, checks)``. Each pin is
        ``(row, col, dir_row, dir_col)`` for a friendly piece pinned to the
        king. Each check is ``(row, col, dir_row, dir_col)`` for an enemy piece
        giving check, with the direction from the king to that piece.
        """
        pins = []
        checks = []
        in_check = False
        if self.white_to_move:
            enemy, ally = "b", "w"
            start_row, start_col = self.white_king_location
        else:
            enemy, ally = "w", "b"
            start_row, start_col = self.black_king_location

        # Index 0-3 are orthogonal, 4-7 diagonal.
        directions = ROOK_DIRECTIONS + BISHOP_DIRECTIONS
        for j, d in enumerate(directions):
            possible_pin = ()
            for i in range(1, 8):
                end_row, end_col = start_row + d[0] * i, start_col + d[1] * i
                if not on_board(end_row, end_col):
                    break
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == ally and end_piece[1] != "K":
                    if possible_pin == ():
                        possible_pin = (end_row, end_col, d[0], d[1])
                    else:
                        break  # Two friendly pieces in a row: no pin possible.
                elif end_piece[0] == enemy:
                    kind = end_piece[1]
                    # Pawns attack diagonally forward: white pawns sit below a
                    # black king (directions 6-7), black pawns above a white king (4-5).
                    pawn_attack = i == 1 and kind == "P" and (
                        (enemy == "w" and 6 <= j <= 7) or (enemy == "b" and 4 <= j <= 5)
                    )
                    if (
                        (0 <= j <= 3 and kind == "R")
                        or (4 <= j <= 7 and kind == "B")
                        or kind == "Q"
                        or pawn_attack
                        or (i == 1 and kind == "K")
                    ):
                        if possible_pin == ():
                            in_check = True
                            checks.append((end_row, end_col, d[0], d[1]))
                        else:
                            pins.append(possible_pin)
                    break

        for dr, dc in KNIGHT_OFFSETS:
            end_row, end_col = start_row + dr, start_col + dc
            if on_board(end_row, end_col) and self.board[end_row][end_col] == enemy + "N":
                in_check = True
                checks.append((end_row, end_col, dr, dc))

        return in_check, pins, checks


class Move:
    """A move from one square to another, with the pieces involved."""

    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq: tuple[int, int], end_sq: tuple[int, int], board: list[list[str]]) -> None:
        self.start_row, self.start_col = start_sq
        self.end_row, self.end_col = end_sq
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Move) and self.move_id == other.move_id

    def __hash__(self) -> int:
        return self.move_id

    def __repr__(self) -> str:
        return f"Move({self.get_chess_notation()})"

    def get_chess_notation(self) -> str:
        """Coordinate notation, e.g. ``e2e4``."""
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r: int, c: int) -> str:
        return self.cols_to_files[c] + self.rows_to_ranks[r]

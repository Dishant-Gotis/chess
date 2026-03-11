import copy
from .constants import (
    WHITE, BLACK, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING,
    INITIAL_BOARD
)


class Board:
    """Represents the chess board state."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset to initial position."""
        self.squares = copy.deepcopy(INITIAL_BOARD)
        self.active_color = WHITE
        self.castling_rights = {
            WHITE: {"kingside": True, "queenside": True},
            BLACK: {"kingside": True, "queenside": True},
        }
        self.en_passant_target = None  # (row, col) or None
        self.halfmove_clock = 0
        self.fullmove_number = 1
        self.move_history = []
        self.position_history = []  # for threefold repetition
        self._record_position()

        # Cache king positions
        self.king_positions = {
            WHITE: (7, 4),
            BLACK: (0, 4),
        }

    def get_piece(self, row, col):
        """Get piece at (row, col). Returns (color, type) tuple or None."""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.squares[row][col]
        return None

    def set_piece(self, row, col, piece):
        """Set piece at (row, col). piece is (color, type) or None."""
        self.squares[row][col] = piece
        if piece and piece[1] == KING:
            self.king_positions[piece[0]] = (row, col)

    def is_empty(self, row, col):
        """Check if square is empty."""
        return self.get_piece(row, col) is None

    def is_in_bounds(self, row, col):
        """Check if coordinates are within the board."""
        return 0 <= row < 8 and 0 <= col < 8

    def clone(self):
        """Create a deep copy of the board."""
        new_board = Board.__new__(Board)
        new_board.squares = [row[:] for row in self.squares]
        new_board.active_color = self.active_color
        new_board.castling_rights = {
            WHITE: dict(self.castling_rights[WHITE]),
            BLACK: dict(self.castling_rights[BLACK]),
        }
        new_board.en_passant_target = self.en_passant_target
        new_board.halfmove_clock = self.halfmove_clock
        new_board.fullmove_number = self.fullmove_number
        new_board.move_history = list(self.move_history)
        new_board.position_history = list(self.position_history)
        new_board.king_positions = dict(self.king_positions)
        return new_board

    def make_move(self, move):
        """
        Apply a move to the board.

        move = {
            "from": (row, col),
            "to": (row, col),
            "promotion": piece_type or None,
        }

        Returns the move record with captured piece info for undo.
        """
        fr, fc = move["from"]
        tr, tc = move["to"]
        piece = self.get_piece(fr, fc)

        if piece is None:
            return None

        color, piece_type = piece
        captured = self.get_piece(tr, tc)

        # Build move record for history & undo
        record = {
            "from": (fr, fc),
            "to": (tr, tc),
            "piece": piece,
            "captured": captured,
            "promotion": move.get("promotion"),
            "prev_castling": {
                WHITE: dict(self.castling_rights[WHITE]),
                BLACK: dict(self.castling_rights[BLACK]),
            },
            "prev_en_passant": self.en_passant_target,
            "prev_halfmove": self.halfmove_clock,
            "flags": {},
        }

        # --- Handle special moves ---

        # En passant capture
        if piece_type == PAWN and (tr, tc) == self.en_passant_target:
            # Capture the pawn that's actually on an adjacent square
            captured_row = fr  # The captured pawn is on the same rank as our pawn
            self.set_piece(captured_row, tc, None)
            record["flags"]["en_passant"] = True
            record["captured"] = (BLACK if color == WHITE else WHITE, PAWN)

        # Castling
        if piece_type == KING and abs(fc - tc) == 2:
            record["flags"]["castling"] = True
            if tc == 6:  # Kingside
                rook = self.get_piece(fr, 7)
                self.set_piece(fr, 7, None)
                self.set_piece(fr, 5, rook)
                record["flags"]["castling_side"] = "kingside"
            elif tc == 2:  # Queenside
                rook = self.get_piece(fr, 0)
                self.set_piece(fr, 0, None)
                self.set_piece(fr, 3, rook)
                record["flags"]["castling_side"] = "queenside"

        # Move the piece
        self.set_piece(fr, fc, None)

        # Promotion
        if piece_type == PAWN and (tr == 0 or tr == 7):
            promo_type = move.get("promotion", QUEEN)
            self.set_piece(tr, tc, (color, promo_type))
            record["flags"]["promotion"] = True
        else:
            self.set_piece(tr, tc, piece)

        # Update en passant target
        if piece_type == PAWN and abs(fr - tr) == 2:
            self.en_passant_target = ((fr + tr) // 2, fc)
        else:
            self.en_passant_target = None

        # Update castling rights
        # If king moves, lose both castling rights
        if piece_type == KING:
            self.castling_rights[color]["kingside"] = False
            self.castling_rights[color]["queenside"] = False

        # If rook moves or is captured, lose that side's right
        if piece_type == ROOK:
            if fr == 0 and fc == 0:
                self.castling_rights[BLACK]["queenside"] = False
            elif fr == 0 and fc == 7:
                self.castling_rights[BLACK]["kingside"] = False
            elif fr == 7 and fc == 0:
                self.castling_rights[WHITE]["queenside"] = False
            elif fr == 7 and fc == 7:
                self.castling_rights[WHITE]["kingside"] = False

        if captured and captured[1] == ROOK:
            if tr == 0 and tc == 0:
                self.castling_rights[BLACK]["queenside"] = False
            elif tr == 0 and tc == 7:
                self.castling_rights[BLACK]["kingside"] = False
            elif tr == 7 and tc == 0:
                self.castling_rights[WHITE]["queenside"] = False
            elif tr == 7 and tc == 7:
                self.castling_rights[WHITE]["kingside"] = False

        # Update clocks
        if piece_type == PAWN or captured:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        if color == BLACK:
            self.fullmove_number += 1

        # Switch turn
        self.active_color = BLACK if color == WHITE else WHITE

        # Save to history
        self.move_history.append(record)
        self._record_position()

        return record

    def unmake_move(self):
        """Undo the last move."""
        if not self.move_history:
            return None

        record = self.move_history.pop()
        self.position_history.pop()

        fr, fc = record["from"]
        tr, tc = record["to"]
        piece = record["piece"]

        # Restore piece to original square
        self.set_piece(fr, fc, piece)

        # Restore captured piece or clear the target square
        if record["flags"].get("en_passant"):
            self.set_piece(tr, tc, None)
            # Restore the en-passant captured pawn
            captured_row = fr
            opponent_color = BLACK if piece[0] == WHITE else WHITE
            self.set_piece(captured_row, tc, (opponent_color, PAWN))
        else:
            self.set_piece(tr, tc, record["captured"])

        # Undo castling rook move
        if record["flags"].get("castling"):
            if record["flags"]["castling_side"] == "kingside":
                rook = self.get_piece(fr, 5)
                self.set_piece(fr, 5, None)
                self.set_piece(fr, 7, rook)
            elif record["flags"]["castling_side"] == "queenside":
                rook = self.get_piece(fr, 3)
                self.set_piece(fr, 3, None)
                self.set_piece(fr, 0, rook)

        # Restore state
        self.castling_rights = {
            WHITE: dict(record["prev_castling"][WHITE]),
            BLACK: dict(record["prev_castling"][BLACK]),
        }
        self.en_passant_target = record["prev_en_passant"]
        self.halfmove_clock = record["prev_halfmove"]

        if piece[0] == BLACK:
            self.fullmove_number -= 1

        self.active_color = piece[0]

        return record

    def _record_position(self):
        """Record current position for threefold repetition detection."""
        pos_key = self._position_key()
        self.position_history.append(pos_key)

    def _position_key(self):
        """Generate a hashable key for the current position."""
        pieces = tuple(tuple(row) for row in self.squares)
        castling = (
            self.castling_rights[WHITE]["kingside"],
            self.castling_rights[WHITE]["queenside"],
            self.castling_rights[BLACK]["kingside"],
            self.castling_rights[BLACK]["queenside"],
        )
        return (pieces, self.active_color, castling, self.en_passant_target)

    def to_dict(self):
        """Convert board state to serializable dict for API responses."""
        squares = []
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece:
                    squares.append({
                        "row": row,
                        "col": col,
                        "color": piece[0],
                        "type": piece[1],
                    })
        return {
            "pieces": squares,
            "activeColor": self.active_color,
            "castlingRights": self.castling_rights,
            "enPassantTarget": self.en_passant_target,
            "halfmoveClock": self.halfmove_clock,
            "fullmoveNumber": self.fullmove_number,
        }

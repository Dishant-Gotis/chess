from .constants import (
    WHITE, BLACK, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING,
    KNIGHT_MOVES, BISHOP_DIRS, ROOK_DIRS, QUEEN_DIRS, KING_DIRS
)


def generate_pseudo_moves(board, color):
    """Generate all pseudo-legal moves for the given color.
    These may leave the king in check — filtering happens in validation.py.
    """
    moves = []
    for row in range(8):
        for col in range(8):
            piece = board.get_piece(row, col)
            if piece and piece[0] == color:
                piece_type = piece[1]
                if piece_type == PAWN:
                    moves.extend(_pawn_moves(board, row, col, color))
                elif piece_type == KNIGHT:
                    moves.extend(_knight_moves(board, row, col, color))
                elif piece_type == BISHOP:
                    moves.extend(_sliding_moves(board, row, col, color, BISHOP_DIRS))
                elif piece_type == ROOK:
                    moves.extend(_sliding_moves(board, row, col, color, ROOK_DIRS))
                elif piece_type == QUEEN:
                    moves.extend(_sliding_moves(board, row, col, color, QUEEN_DIRS))
                elif piece_type == KING:
                    moves.extend(_king_moves(board, row, col, color))
    return moves


def generate_captures(board, color):
    """Generate only capture moves — used for quiescence search in AI."""
    moves = []
    for row in range(8):
        for col in range(8):
            piece = board.get_piece(row, col)
            if piece and piece[0] == color:
                piece_type = piece[1]
                if piece_type == PAWN:
                    moves.extend(_pawn_captures(board, row, col, color))
                elif piece_type == KNIGHT:
                    moves.extend(_knight_captures(board, row, col, color))
                elif piece_type == BISHOP:
                    moves.extend(_sliding_captures(board, row, col, color, BISHOP_DIRS))
                elif piece_type == ROOK:
                    moves.extend(_sliding_captures(board, row, col, color, ROOK_DIRS))
                elif piece_type == QUEEN:
                    moves.extend(_sliding_captures(board, row, col, color, QUEEN_DIRS))
                elif piece_type == KING:
                    moves.extend(_king_captures(board, row, col, color))
    return moves


def _pawn_moves(board, row, col, color):
    """Generate all pawn moves including pushes, captures, en passant, promotion."""
    moves = []
    direction = -1 if color == WHITE else 1
    start_row = 6 if color == WHITE else 1
    promo_row = 0 if color == WHITE else 7

    # Single push
    nr = row + direction
    if board.is_in_bounds(nr, col) and board.is_empty(nr, col):
        if nr == promo_row:
            for promo in [QUEEN, ROOK, BISHOP, KNIGHT]:
                moves.append({"from": (row, col), "to": (nr, col), "promotion": promo})
        else:
            moves.append({"from": (row, col), "to": (nr, col)})

        # Double push from start
        nr2 = row + 2 * direction
        if row == start_row and board.is_empty(nr2, col):
            moves.append({"from": (row, col), "to": (nr2, col)})

    # Captures (diagonal)
    for dc in [-1, 1]:
        nc = col + dc
        nr = row + direction
        if not board.is_in_bounds(nr, nc):
            continue
        target = board.get_piece(nr, nc)
        if target and target[0] != color:
            if nr == promo_row:
                for promo in [QUEEN, ROOK, BISHOP, KNIGHT]:
                    moves.append({"from": (row, col), "to": (nr, nc), "promotion": promo})
            else:
                moves.append({"from": (row, col), "to": (nr, nc)})
        # En passant
        if board.en_passant_target == (nr, nc):
            moves.append({"from": (row, col), "to": (nr, nc)})

    return moves


def _pawn_captures(board, row, col, color):
    """Pawn captures only (for quiescence search)."""
    moves = []
    direction = -1 if color == WHITE else 1
    promo_row = 0 if color == WHITE else 7

    for dc in [-1, 1]:
        nc = col + dc
        nr = row + direction
        if not board.is_in_bounds(nr, nc):
            continue
        target = board.get_piece(nr, nc)
        if target and target[0] != color:
            if nr == promo_row:
                for promo in [QUEEN, ROOK, BISHOP, KNIGHT]:
                    moves.append({"from": (row, col), "to": (nr, nc), "promotion": promo})
            else:
                moves.append({"from": (row, col), "to": (nr, nc)})
        if board.en_passant_target == (nr, nc):
            moves.append({"from": (row, col), "to": (nr, nc)})

    return moves


def _knight_moves(board, row, col, color):
    """Generate all knight moves."""
    moves = []
    for dr, dc in KNIGHT_MOVES:
        nr, nc = row + dr, col + dc
        if board.is_in_bounds(nr, nc):
            target = board.get_piece(nr, nc)
            if target is None or target[0] != color:
                moves.append({"from": (row, col), "to": (nr, nc)})
    return moves


def _knight_captures(board, row, col, color):
    """Knight captures only."""
    moves = []
    for dr, dc in KNIGHT_MOVES:
        nr, nc = row + dr, col + dc
        if board.is_in_bounds(nr, nc):
            target = board.get_piece(nr, nc)
            if target and target[0] != color:
                moves.append({"from": (row, col), "to": (nr, nc)})
    return moves


def _sliding_moves(board, row, col, color, directions):
    """Generate moves for sliding pieces (bishop, rook, queen)."""
    moves = []
    for dr, dc in directions:
        nr, nc = row + dr, col + dc
        while board.is_in_bounds(nr, nc):
            target = board.get_piece(nr, nc)
            if target is None:
                moves.append({"from": (row, col), "to": (nr, nc)})
            elif target[0] != color:
                moves.append({"from": (row, col), "to": (nr, nc)})
                break
            else:
                break
            nr += dr
            nc += dc
    return moves


def _sliding_captures(board, row, col, color, directions):
    """Sliding piece captures only."""
    moves = []
    for dr, dc in directions:
        nr, nc = row + dr, col + dc
        while board.is_in_bounds(nr, nc):
            target = board.get_piece(nr, nc)
            if target is None:
                nr += dr
                nc += dc
                continue
            elif target[0] != color:
                moves.append({"from": (row, col), "to": (nr, nc)})
            break
    return moves


def _king_moves(board, row, col, color):
    """Generate king moves including castling."""
    moves = []
    for dr, dc in KING_DIRS:
        nr, nc = row + dr, col + dc
        if board.is_in_bounds(nr, nc):
            target = board.get_piece(nr, nc)
            if target is None or target[0] != color:
                moves.append({"from": (row, col), "to": (nr, nc)})

    # Castling
    moves.extend(_castling_moves(board, row, col, color))

    return moves


def _king_captures(board, row, col, color):
    """King captures only."""
    moves = []
    for dr, dc in KING_DIRS:
        nr, nc = row + dr, col + dc
        if board.is_in_bounds(nr, nc):
            target = board.get_piece(nr, nc)
            if target and target[0] != color:
                moves.append({"from": (row, col), "to": (nr, nc)})
    return moves


def _castling_moves(board, row, col, color):
    """Generate castling moves if legal."""
    moves = []
    opponent = BLACK if color == WHITE else WHITE

    # Can't castle while in check
    if is_square_attacked(board, row, col, opponent):
        return moves

    # Kingside
    if board.castling_rights[color]["kingside"]:
        if (board.is_empty(row, 5) and board.is_empty(row, 6)):
            # Squares the king passes through must not be attacked
            if (not is_square_attacked(board, row, 5, opponent) and
                    not is_square_attacked(board, row, 6, opponent)):
                moves.append({"from": (row, col), "to": (row, 6)})

    # Queenside
    if board.castling_rights[color]["queenside"]:
        if (board.is_empty(row, 3) and board.is_empty(row, 2) and
                board.is_empty(row, 1)):
            if (not is_square_attacked(board, row, 3, opponent) and
                    not is_square_attacked(board, row, 2, opponent)):
                moves.append({"from": (row, col), "to": (row, 2)})

    return moves


def is_square_attacked(board, row, col, by_color):
    """Check if a square is attacked by any piece of the given color.
    More efficient than generating all moves — checks from the target outward.
    """
    # Check knight attacks
    for dr, dc in KNIGHT_MOVES:
        nr, nc = row + dr, col + dc
        if board.is_in_bounds(nr, nc):
            piece = board.get_piece(nr, nc)
            if piece and piece[0] == by_color and piece[1] == KNIGHT:
                return True

    # Check sliding attacks (bishop/queen on diagonals, rook/queen on straights)
    for dr, dc in BISHOP_DIRS:
        nr, nc = row + dr, col + dc
        while board.is_in_bounds(nr, nc):
            piece = board.get_piece(nr, nc)
            if piece:
                if piece[0] == by_color and piece[1] in (BISHOP, QUEEN):
                    return True
                break
            nr += dr
            nc += dc

    for dr, dc in ROOK_DIRS:
        nr, nc = row + dr, col + dc
        while board.is_in_bounds(nr, nc):
            piece = board.get_piece(nr, nc)
            if piece:
                if piece[0] == by_color and piece[1] in (ROOK, QUEEN):
                    return True
                break
            nr += dr
            nc += dc

    # Check pawn attacks
    pawn_dir = 1 if by_color == WHITE else -1  # Direction pawns attack FROM
    for dc in [-1, 1]:
        nr, nc = row + pawn_dir, col + dc
        if board.is_in_bounds(nr, nc):
            piece = board.get_piece(nr, nc)
            if piece and piece[0] == by_color and piece[1] == PAWN:
                return True

    # Check king attacks (for adjacent king detection)
    for dr, dc in KING_DIRS:
        nr, nc = row + dr, col + dc
        if board.is_in_bounds(nr, nc):
            piece = board.get_piece(nr, nc)
            if piece and piece[0] == by_color and piece[1] == KING:
                return True

    return False

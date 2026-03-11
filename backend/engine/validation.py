from .constants import WHITE, BLACK, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING
from .moves import generate_pseudo_moves, is_square_attacked


def generate_legal_moves(board, color=None):
    """Generate all legal moves for the given color (defaults to active color).
    Filters out moves that would leave the king in check.
    """
    if color is None:
        color = board.active_color

    pseudo_moves = generate_pseudo_moves(board, color)
    legal_moves = []

    for move in pseudo_moves:
        # Make the move on a clone
        test_board = board.clone()
        test_board.make_move(move)

        # Check if our king is safe after the move
        king_pos = test_board.king_positions[color]
        opponent = BLACK if color == WHITE else WHITE

        if not is_square_attacked(test_board, king_pos[0], king_pos[1], opponent):
            legal_moves.append(move)

    return legal_moves


def get_legal_moves_for_square(board, row, col):
    """Get legal moves for a specific piece at (row, col)."""
    piece = board.get_piece(row, col)
    if not piece:
        return []

    color = piece[0]
    all_legal = generate_legal_moves(board, color)

    return [m for m in all_legal if m["from"] == (row, col)]


def is_in_check(board, color=None):
    """Check if the given color's king is in check."""
    if color is None:
        color = board.active_color
    king_pos = board.king_positions[color]
    opponent = BLACK if color == WHITE else WHITE
    return is_square_attacked(board, king_pos[0], king_pos[1], opponent)


def is_checkmate(board, color=None):
    """Check if the given color is in checkmate."""
    if color is None:
        color = board.active_color
    return is_in_check(board, color) and len(generate_legal_moves(board, color)) == 0


def is_stalemate(board, color=None):
    """Check if the given color is in stalemate."""
    if color is None:
        color = board.active_color
    return not is_in_check(board, color) and len(generate_legal_moves(board, color)) == 0


def is_insufficient_material(board):
    """Check for draw by insufficient material."""
    pieces = {WHITE: [], BLACK: []}
    for row in range(8):
        for col in range(8):
            piece = board.get_piece(row, col)
            if piece and piece[1] != KING:
                pieces[piece[0]].append((piece[1], row, col))

    w, b = pieces[WHITE], pieces[BLACK]

    # King vs King
    if len(w) == 0 and len(b) == 0:
        return True
    # King + minor piece vs King
    if len(w) == 0 and len(b) == 1 and b[0][0] in (KNIGHT, BISHOP):
        return True
    if len(b) == 0 and len(w) == 1 and w[0][0] in (KNIGHT, BISHOP):
        return True
    # King + Bishop vs King + Bishop (same color bishops)
    if (len(w) == 1 and len(b) == 1 and
            w[0][0] == BISHOP and b[0][0] == BISHOP):
        w_light = (w[0][1] + w[0][2]) % 2
        b_light = (b[0][1] + b[0][2]) % 2
        if w_light == b_light:
            return True

    return False


def is_fifty_move_rule(board):
    """Check for draw by fifty-move rule."""
    return board.halfmove_clock >= 100  # 100 half-moves = 50 full moves


def is_threefold_repetition(board):
    """Check for draw by threefold repetition."""
    if len(board.position_history) < 3:
        return False
    current = board.position_history[-1]
    count = board.position_history.count(current)
    return count >= 3


def get_game_status(board):
    """
    Get the current game status.
    Returns a dict with:
        - status: "playing", "checkmate", "stalemate", "draw"
        - winner: "white", "black", or None
        - reason: human-readable reason
        - inCheck: bool
    """
    active = board.active_color
    in_check = is_in_check(board, active)

    if is_checkmate(board, active):
        winner = BLACK if active == WHITE else WHITE
        return {
            "status": "checkmate",
            "winner": winner,
            "reason": f"Checkmate! {winner.capitalize()} wins.",
            "inCheck": True,
        }

    if is_stalemate(board, active):
        return {
            "status": "stalemate",
            "winner": None,
            "reason": "Stalemate! The game is a draw.",
            "inCheck": False,
        }

    if is_insufficient_material(board):
        return {
            "status": "draw",
            "winner": None,
            "reason": "Draw by insufficient material.",
            "inCheck": False,
        }

    if is_fifty_move_rule(board):
        return {
            "status": "draw",
            "winner": None,
            "reason": "Draw by fifty-move rule.",
            "inCheck": False,
        }

    if is_threefold_repetition(board):
        return {
            "status": "draw",
            "winner": None,
            "reason": "Draw by threefold repetition.",
            "inCheck": False,
        }

    return {
        "status": "playing",
        "winner": None,
        "reason": None,
        "inCheck": in_check,
    }

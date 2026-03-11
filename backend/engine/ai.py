import random
from .constants import (
    WHITE, BLACK, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING,
    PIECE_VALUES, PST
)
from .moves import generate_pseudo_moves, is_square_attacked
from .validation import generate_legal_moves, is_in_check


# Depth settings per difficulty
DIFFICULTY_DEPTH = {
    "easy": 2,
    "medium": 3,
    "hard": 4,
}


def get_best_move(board, difficulty="medium"):
    """Get the best move for the current player using minimax."""
    depth = DIFFICULTY_DEPTH.get(difficulty, 3)
    color = board.active_color
    legal_moves = generate_legal_moves(board, color)

    if not legal_moves:
        return None

    # Add some randomness for easy mode
    if difficulty == "easy":
        # 30% chance to pick a random move
        if random.random() < 0.3:
            return random.choice(legal_moves)

    best_move = None
    best_score = float("-inf")
    alpha = float("-inf")
    beta = float("inf")

    # Order moves for better pruning
    ordered_moves = _order_moves(board, legal_moves)

    for move in ordered_moves:
        clone = board.clone()
        clone.make_move(move)
        score = -_negamax(clone, depth - 1, -beta, -alpha, _opposite(color))

        if score > best_score:
            best_score = score
            best_move = move
        alpha = max(alpha, score)

    return best_move


def _negamax(board, depth, alpha, beta, color):
    """Negamax search with alpha-beta pruning."""
    if depth == 0:
        return _quiescence(board, alpha, beta, color)

    legal_moves = generate_legal_moves(board, color)

    if not legal_moves:
        if is_in_check(board, color):
            return -20000 - depth  # Checkmate (prefer faster mates)
        return 0  # Stalemate

    ordered_moves = _order_moves(board, legal_moves)

    for move in ordered_moves:
        clone = board.clone()
        clone.make_move(move)
        score = -_negamax(clone, depth - 1, -beta, -alpha, _opposite(color))

        if score >= beta:
            return beta  # Beta cutoff
        alpha = max(alpha, score)

    return alpha


def _quiescence(board, alpha, beta, color):
    """Quiescence search — evaluate captures to avoid horizon effect."""
    stand_pat = _evaluate(board, color)

    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    # Only search captures
    from .moves import generate_captures
    captures = generate_captures(board, color)

    # Filter legal captures
    legal_captures = []
    for move in captures:
        clone = board.clone()
        clone.make_move(move)
        king_pos = clone.king_positions[color]
        opponent = _opposite(color)
        if not is_square_attacked(clone, king_pos[0], king_pos[1], opponent):
            legal_captures.append(move)

    for move in legal_captures:
        clone = board.clone()
        clone.make_move(move)
        score = -_quiescence(clone, -beta, -alpha, _opposite(color))

        if score >= beta:
            return beta
        alpha = max(alpha, score)

    return alpha


def _evaluate(board, color):
    """Evaluate the board position from the perspective of the given color."""
    score = 0
    opponent = _opposite(color)

    for row in range(8):
        for col in range(8):
            piece = board.get_piece(row, col)
            if piece is None:
                continue

            p_color, p_type = piece
            value = PIECE_VALUES[p_type]

            # Piece-square table bonus
            pst = PST.get(p_type)
            if pst:
                if p_color == WHITE:
                    value += pst[row][col]
                else:
                    value += pst[7 - row][col]

            if p_color == color:
                score += value
            else:
                score -= value

    return score


def _order_moves(board, moves):
    """Order moves for better alpha-beta pruning.
    Captures and promotions first, then other moves.
    """
    scored = []
    for move in moves:
        score = 0
        target = board.get_piece(*move["to"])

        # Capture bonus: MVV-LVA (Most Valuable Victim - Least Valuable Attacker)
        if target:
            attacker = board.get_piece(*move["from"])
            score += 10 * PIECE_VALUES[target[1]] - PIECE_VALUES[attacker[1]]

        # Promotion bonus
        if move.get("promotion"):
            score += PIECE_VALUES.get(move["promotion"], 0)

        scored.append((score, move))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scored]


def _opposite(color):
    return BLACK if color == WHITE else WHITE

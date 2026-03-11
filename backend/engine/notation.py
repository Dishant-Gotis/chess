from .constants import PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING


# File letters for algebraic notation
FILES = "abcdefgh"
RANKS = "87654321"

PIECE_LETTERS = {
    KNIGHT: "N",
    BISHOP: "B",
    ROOK: "R",
    QUEEN: "Q",
    KING: "K",
}


def square_to_algebraic(row, col):
    """Convert (row, col) to algebraic notation like 'e4'."""
    return FILES[col] + RANKS[row]


def algebraic_to_square(notation):
    """Convert algebraic notation like 'e4' to (row, col)."""
    col = FILES.index(notation[0])
    row = RANKS.index(notation[1])
    return (row, col)


def move_to_san(board, move):
    """Convert a move to Standard Algebraic Notation (SAN).
    This should be called BEFORE the move is made on the board.
    """
    fr, fc = move["from"]
    tr, tc = move["to"]
    piece = board.get_piece(fr, fc)

    if piece is None:
        return "?"

    color, piece_type = piece
    captured = board.get_piece(tr, tc)
    is_ep = (piece_type == PAWN and board.en_passant_target == (tr, tc))

    # Castling
    if piece_type == KING and abs(fc - tc) == 2:
        return "O-O" if tc == 6 else "O-O-O"

    san = ""

    # Piece letter (pawns have no letter)
    if piece_type != PAWN:
        san += PIECE_LETTERS.get(piece_type, "")

        # Disambiguation: check if another piece of the same type can reach the same square
        from .validation import generate_legal_moves
        all_moves = generate_legal_moves(board, color)
        ambiguous = [
            m for m in all_moves
            if (m["from"] != (fr, fc) and
                m["to"] == (tr, tc) and
                board.get_piece(*m["from"]) and
                board.get_piece(*m["from"])[1] == piece_type)
        ]
        if ambiguous:
            same_file = any(m["from"][1] == fc for m in ambiguous)
            same_rank = any(m["from"][0] == fr for m in ambiguous)
            if not same_file:
                san += FILES[fc]
            elif not same_rank:
                san += RANKS[fr]
            else:
                san += FILES[fc] + RANKS[fr]

    # Pawn capture includes file
    if piece_type == PAWN and (captured or is_ep):
        san += FILES[fc]

    # Capture marker
    if captured or is_ep:
        san += "x"

    # Target square
    san += square_to_algebraic(tr, tc)

    # Promotion
    if move.get("promotion"):
        san += "=" + PIECE_LETTERS.get(move["promotion"], "Q")

    # Check or checkmate marker (need to look ahead)
    test_board = board.clone()
    test_board.make_move(move)
    from .validation import is_in_check, is_checkmate
    opponent = "black" if color == "white" else "white"
    if is_checkmate(test_board, opponent):
        san += "#"
    elif is_in_check(test_board, opponent):
        san += "+"

    return san

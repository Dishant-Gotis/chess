import copy
from .constants import WHITE, BLACK
from .board import Board
from .validation import generate_legal_moves, get_game_status, get_legal_moves_for_square
from .ai import get_best_move
from .notation import move_to_san, square_to_algebraic


class Game:
    """Manages a complete chess game."""

    def __init__(self):
        self.board = Board()
        self.mode = "pvp"  # "pvp" or "ai"
        self.ai_color = BLACK
        self.ai_difficulty = "medium"
        self.move_list = []  # SAN notation list
        self.captured_pieces = {WHITE: [], BLACK: []}
        self.game_over = False
        self.result = None

    def new_game(self, mode="pvp", ai_color=BLACK, ai_difficulty="medium"):
        """Start a new game."""
        self.board = Board()
        self.mode = mode
        self.ai_color = ai_color
        self.ai_difficulty = ai_difficulty
        self.move_list = []
        self.captured_pieces = {WHITE: [], BLACK: []}
        self.game_over = False
        self.result = None

    def make_move(self, from_pos, to_pos, promotion=None):
        """Attempt to make a move. Returns result dict."""
        if self.game_over:
            return {"success": False, "error": "Game is over."}

        fr, fc = from_pos
        tr, tc = to_pos

        # Validate it's the right turn
        piece = self.board.get_piece(fr, fc)
        if not piece or piece[0] != self.board.active_color:
            return {"success": False, "error": "Not your piece."}

        # Check if move is in legal moves
        legal = get_legal_moves_for_square(self.board, fr, fc)
        matching = [m for m in legal if m["to"] == (tr, tc)]

        if not matching:
            return {"success": False, "error": "Illegal move."}

        # Handle promotion
        move = matching[0]
        if promotion:
            move = next((m for m in matching if m.get("promotion") == promotion), matching[0])

        # Check if promotion is needed but not specified
        needs_promotion = any(m.get("promotion") for m in matching)
        if needs_promotion and not promotion:
            return {
                "success": False,
                "needsPromotion": True,
                "from": [fr, fc],
                "to": [tr, tc],
            }

        # Generate SAN before making the move
        san = move_to_san(self.board, move)

        # Track captured piece
        captured = self.board.get_piece(tr, tc)
        if captured:
            self.captured_pieces[captured[0]].append(captured[1])
        # En passant capture
        if (piece[1] == "pawn" and (tr, tc) == self.board.en_passant_target):
            opp = BLACK if piece[0] == WHITE else WHITE
            self.captured_pieces[opp].append("pawn")

        # Make the move
        self.board.make_move(move)
        self.move_list.append(san)

        # Check game status
        status = get_game_status(self.board)
        if status["status"] != "playing":
            self.game_over = True
            self.result = status

        return {
            "success": True,
            "san": san,
            "board": self.board.to_dict(),
            "status": status,
            "capturedPieces": {
                WHITE: self.captured_pieces[WHITE],
                BLACK: self.captured_pieces[BLACK],
            },
            "moveList": self.move_list,
        }

    def get_ai_move(self):
        """Get and execute AI's move."""
        if self.game_over:
            return None
        if self.board.active_color != self.ai_color:
            return None

        move = get_best_move(self.board, self.ai_difficulty)
        if not move:
            return None

        fr, fc = move["from"]
        tr, tc = move["to"]
        promotion = move.get("promotion")

        return self.make_move((fr, fc), (tr, tc), promotion)

    def undo_move(self):
        """Undo the last move (or last two in AI mode)."""
        if not self.board.move_history:
            return False

        self.board.unmake_move()
        if self.move_list:
            self.move_list.pop()

        # In AI mode, undo AI's move too
        if self.mode == "ai" and self.board.move_history:
            self.board.unmake_move()
            if self.move_list:
                self.move_list.pop()

        self.game_over = False
        self.result = None

        # Rebuild captured pieces
        self._rebuild_captured()
        return True

    def _rebuild_captured(self):
        """Rebuild captured pieces list from move history."""
        self.captured_pieces = {WHITE: [], BLACK: []}
        for record in self.board.move_history:
            if record["captured"]:
                cap_color = record["captured"][0]
                cap_type = record["captured"][1]
                self.captured_pieces[cap_color].append(cap_type)

    def get_state(self):
        """Get full game state for the frontend."""
        status = get_game_status(self.board)
        legal_moves_map = {}

        if not self.game_over:
            all_legal = generate_legal_moves(self.board)
            for move in all_legal:
                key = f"{move['from'][0]},{move['from'][1]}"
                if key not in legal_moves_map:
                    legal_moves_map[key] = []
                legal_moves_map[key].append({
                    "to": list(move["to"]),
                    "promotion": move.get("promotion"),
                })

        return {
            "board": self.board.to_dict(),
            "activeColor": self.board.active_color,
            "status": status,
            "legalMoves": legal_moves_map,
            "moveList": self.move_list,
            "capturedPieces": {
                WHITE: self.captured_pieces[WHITE],
                BLACK: self.captured_pieces[BLACK],
            },
            "mode": self.mode,
            "aiColor": self.ai_color,
            "gameOver": self.game_over,
        }

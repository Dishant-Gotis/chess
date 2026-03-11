from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from engine.game import Game
from engine.constants import WHITE, BLACK

app = FastAPI(title="Chess App API")

# CORS for development (Vite runs on different port)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Game instance (single-player server)
game = Game()

# --- Pydantic Models ---

class NewGameRequest(BaseModel):
    mode: str = "pvp"           # "pvp" or "ai"
    aiColor: str = "black"      # "white" or "black"
    aiDifficulty: str = "medium"  # "easy", "medium", "hard"

class MoveRequest(BaseModel):
    fromRow: int
    fromCol: int
    toRow: int
    toCol: int
    promotion: Optional[str] = None

# --- API Endpoints ---

@app.get("/api/state")
def get_state():
    """Get the current game state."""
    return game.get_state()


@app.post("/api/new-game")
def new_game(req: NewGameRequest):
    """Start a new game."""
    ai_color = BLACK if req.aiColor == "black" else WHITE
    game.new_game(
        mode=req.mode,
        ai_color=ai_color,
        ai_difficulty=req.aiDifficulty,
    )

    state = game.get_state()

    # If AI plays white, make its first move
    if req.mode == "ai" and ai_color == WHITE:
        ai_result = game.get_ai_move()
        state = game.get_state()

    return state


@app.post("/api/move")
def make_move(req: MoveRequest):
    """Make a player move."""
    result = game.make_move(
        from_pos=(req.fromRow, req.fromCol),
        to_pos=(req.toRow, req.toCol),
        promotion=req.promotion,
    )

    if not result.get("success"):
        return result

    response = {
        "playerMove": result,
        "state": game.get_state(),
        "aiMove": None,
    }

    # If AI mode and game not over, get AI response
    if game.mode == "ai" and not game.game_over:
        ai_result = game.get_ai_move()
        if ai_result:
            response["aiMove"] = ai_result
            response["state"] = game.get_state()

    return response


@app.post("/api/undo")
def undo_move():
    """Undo the last move."""
    success = game.undo_move()
    return {
        "success": success,
        "state": game.get_state(),
    }


@app.post("/api/resign")
def resign():
    """Current player resigns."""
    winner = BLACK if game.board.active_color == WHITE else WHITE
    game.game_over = True
    game.result = {
        "status": "resigned",
        "winner": winner,
        "reason": f"{game.board.active_color.capitalize()} resigned. {winner.capitalize()} wins!",
        "inCheck": False,
    }
    return game.get_state()

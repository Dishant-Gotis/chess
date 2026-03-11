/**
 * API client for communicating with the FastAPI backend
 */
const BASE = '';

async function request(path, options = {}) {
    const url = `${BASE}${path}`;
    const res = await fetch(url, {
        headers: { 'Content-Type': 'application/json' },
        ...options,
    });
    if (!res.ok) {
        throw new Error(`API error: ${res.status}`);
    }
    return res.json();
}

export const api = {
    getState() {
        return request('/api/state');
    },

    newGame(mode = 'pvp', aiColor = 'black', aiDifficulty = 'medium') {
        return request('/api/new-game', {
            method: 'POST',
            body: JSON.stringify({ mode, aiColor, aiDifficulty }),
        });
    },

    makeMove(fromRow, fromCol, toRow, toCol, promotion = null) {
        return request('/api/move', {
            method: 'POST',
            body: JSON.stringify({ fromRow, fromCol, toRow, toCol, promotion }),
        });
    },

    undo() {
        return request('/api/undo', { method: 'POST' });
    },

    resign() {
        return request('/api/resign', { method: 'POST' });
    },
};

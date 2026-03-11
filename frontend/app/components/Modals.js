'use client';

import { useState } from 'react';
import './Modals.css';

export function NewGameModal({ isOpen, onClose, onStart }) {
    const [mode, setMode] = useState('pvp');
    const [difficulty, setDifficulty] = useState('medium');
    const [playerColor, setPlayerColor] = useState('white');

    if (!isOpen) return null;

    const handleStart = () => {
        const aiColor = playerColor === 'white' ? 'black' : 'white';
        onStart({ mode, aiColor, difficulty });
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal" onClick={e => e.stopPropagation()}>
                <h2 className="modal-title">New Game</h2>
                <div className="modal-body">
                    <div className="form-group">
                        <label className="form-label">Game Mode</label>
                        <div className="toggle-group">
                            <button
                                className={`toggle-btn${mode === 'pvp' ? ' active' : ''}`}
                                onClick={() => setMode('pvp')}
                            >
                                Player vs Player
                            </button>
                            <button
                                className={`toggle-btn${mode === 'ai' ? ' active' : ''}`}
                                onClick={() => setMode('ai')}
                            >
                                Player vs AI
                            </button>
                        </div>
                    </div>

                    {mode === 'ai' && (
                        <>
                            <div className="form-group">
                                <label className="form-label">Difficulty</label>
                                <div className="toggle-group">
                                    {['easy', 'medium', 'hard'].map(d => (
                                        <button
                                            key={d}
                                            className={`toggle-btn${difficulty === d ? ' active' : ''}`}
                                            onClick={() => setDifficulty(d)}
                                        >
                                            {d.charAt(0).toUpperCase() + d.slice(1)}
                                        </button>
                                    ))}
                                </div>
                            </div>
                            <div className="form-group">
                                <label className="form-label">Play as</label>
                                <div className="toggle-group">
                                    <button
                                        className={`toggle-btn${playerColor === 'white' ? ' active' : ''}`}
                                        onClick={() => setPlayerColor('white')}
                                    >
                                        ♔ White
                                    </button>
                                    <button
                                        className={`toggle-btn${playerColor === 'black' ? ' active' : ''}`}
                                        onClick={() => setPlayerColor('black')}
                                    >
                                        ♚ Black
                                    </button>
                                </div>
                            </div>
                        </>
                    )}
                </div>
                <div className="modal-footer">
                    <button className="btn btn-primary btn-lg" onClick={handleStart}>
                        Start Game
                    </button>
                    <button className="btn btn-ghost" onClick={onClose}>Cancel</button>
                </div>
            </div>
        </div>
    );
}

export function PromotionModal({ isOpen, color, onSelect }) {
    if (!isOpen) return null;

    const pieces = color === 'white'
        ? { queen: '♕', rook: '♖', bishop: '♗', knight: '♘' }
        : { queen: '♛', rook: '♜', bishop: '♝', knight: '♞' };

    return (
        <div className="modal-overlay">
            <div className="modal modal-sm">
                <h2 className="modal-title">Promote Pawn</h2>
                <div className="promotion-choices">
                    {Object.entries(pieces).map(([type, symbol]) => (
                        <button
                            key={type}
                            className="promo-btn"
                            onClick={() => onSelect(type)}
                        >
                            {symbol}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}

export function GameOverModal({ isOpen, title, reason, onPlayAgain, onClose }) {
    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal" onClick={e => e.stopPropagation()}>
                <h2 className="modal-title">{title}</h2>
                <p className="gameover-reason">{reason}</p>
                <div className="modal-footer">
                    <button className="btn btn-primary btn-lg" onClick={onPlayAgain}>
                        Play Again
                    </button>
                    <button className="btn btn-ghost" onClick={onClose}>
                        Review Board
                    </button>
                </div>
            </div>
        </div>
    );
}

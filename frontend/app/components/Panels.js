'use client';

import { useEffect, useRef } from 'react';
import './Panels.css';

const PIECE_UNICODE = {
    king: '♚', queen: '♛', rook: '♜', bishop: '♝', knight: '♞', pawn: '♟',
};
const PIECE_ORDER = ['queen', 'rook', 'bishop', 'knight', 'pawn'];

export function PlayerCard({ color, name, label, active, capturedPieces = [] }) {
    const sorted = [...capturedPieces].sort(
        (a, b) => PIECE_ORDER.indexOf(a) - PIECE_ORDER.indexOf(b)
    );

    return (
        <div className={`player-card${active ? ' active' : ''}`}>
            <div className="player-info">
                <div className={`player-color-dot ${color}-dot`} />
                <div>
                    <span className="player-name">{name}</span>
                    {label && <div className="player-label">{label}</div>}
                </div>
            </div>
            <div className="captured-pieces">
                {sorted.length === 0 && (
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontStyle: 'italic' }}>
                        No captures
                    </span>
                )}
                {sorted.map((type, i) => (
                    <span key={i} className="captured-piece-icon">
                        {PIECE_UNICODE[type] || '?'}
                    </span>
                ))}
            </div>
        </div>
    );
}

export function MoveHistory({ moves = [] }) {
    const listRef = useRef(null);

    useEffect(() => {
        if (listRef.current) {
            listRef.current.scrollTop = listRef.current.scrollHeight;
        }
    }, [moves]);

    return (
        <div className="move-history-card">
            <h3 className="card-title">Move History</h3>
            <div className="move-list" ref={listRef}>
                {moves.length === 0 ? (
                    <div className="move-placeholder">Play a move to begin...</div>
                ) : (
                    Array.from({ length: Math.ceil(moves.length / 2) }, (_, i) => (
                        <div key={i} className="move-row">
                            <span className="move-number">{i + 1}.</span>
                            <span className="move-san">{moves[i * 2]}</span>
                            {moves[i * 2 + 1] && (
                                <span className="move-san">{moves[i * 2 + 1]}</span>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}

'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import './ChessBoard.css';

const PIECE_UNICODE = {
    white: { king: '♔', queen: '♕', rook: '♖', bishop: '♗', knight: '♘', pawn: '♙' },
    black: { king: '♚', queen: '♛', rook: '♜', bishop: '♝', knight: '♞', pawn: '♟' },
};

const FILES = 'abcdefgh';
const RANKS = '87654321';

export default function ChessBoard({
    boardData,
    legalMoves = {},
    activeColor,
    status,
    flipped = false,
    onMove,
    disabled = false,
}) {
    const [selectedSquare, setSelectedSquare] = useState(null);
    const [legalTargets, setLegalTargets] = useState([]);
    const [isDragging, setIsDragging] = useState(false);
    const [dragFrom, setDragFrom] = useState(null);
    const [ghostPos, setGhostPos] = useState({ x: 0, y: 0 });
    const [ghostPiece, setGhostPiece] = useState(null);
    const [lastMove, setLastMove] = useState(null);
    const [shaking, setShaking] = useState(false);
    const boardRef = useRef(null);

    // Track last move from board history
    useEffect(() => {
        if (boardData?.lastFrom && boardData?.lastTo) {
            setLastMove({ from: boardData.lastFrom, to: boardData.lastTo });
        }
    }, [boardData]);

    // Build piece map from board data
    const pieceMap = {};
    if (boardData?.pieces) {
        for (const p of boardData.pieces) {
            pieceMap[`${p.row},${p.col}`] = p;
        }
    }

    const getSquareInfo = (row, col) => {
        const isLight = (row + col) % 2 === 0;
        const key = `${row},${col}`;
        const piece = pieceMap[key] || null;
        const isSelected = selectedSquare && selectedSquare[0] === row && selectedSquare[1] === col;
        const isLegalTarget = legalTargets.some(m => m.to[0] === row && m.to[1] === col);
        const isLastMove = lastMove && (
            (lastMove.from[0] === row && lastMove.from[1] === col) ||
            (lastMove.to[0] === row && lastMove.to[1] === col)
        );
        const isCheck = status?.inCheck && piece?.type === 'king' && piece?.color === activeColor;

        return { isLight, piece, isSelected, isLegalTarget, isLastMove, isCheck, hasPiece: !!piece };
    };

    const handleSquareClick = useCallback((row, col) => {
        if (disabled || isDragging) return;

        if (selectedSquare) {
            const isLegal = legalTargets.some(m => m.to[0] === row && m.to[1] === col);
            if (isLegal) {
                onMove?.(selectedSquare[0], selectedSquare[1], row, col);
                setSelectedSquare(null);
                setLegalTargets([]);
                setLastMove({ from: selectedSquare, to: [row, col] });
                return;
            }
            if (selectedSquare[0] === row && selectedSquare[1] === col) {
                setSelectedSquare(null);
                setLegalTargets([]);
                return;
            }
        }

        // Select new piece
        const key = `${row},${col}`;
        const moves = legalMoves[key];
        if (moves && moves.length > 0) {
            setSelectedSquare([row, col]);
            setLegalTargets(moves);
        } else {
            setSelectedSquare(null);
            setLegalTargets([]);
        }
    }, [disabled, isDragging, selectedSquare, legalTargets, legalMoves, onMove]);

    // Drag handlers
    const handleMouseDown = useCallback((e, row, col) => {
        if (disabled || e.button !== 0) return;
        const key = `${row},${col}`;
        const moves = legalMoves[key];
        if (!moves || moves.length === 0) return;

        const piece = pieceMap[key];
        if (!piece) return;

        e.preventDefault();
        setIsDragging(true);
        setDragFrom([row, col]);
        setSelectedSquare([row, col]);
        setLegalTargets(moves);
        setGhostPiece(piece);
        setGhostPos({ x: e.clientX - 30, y: e.clientY - 30 });
    }, [disabled, legalMoves, pieceMap]);

    useEffect(() => {
        if (!isDragging) return;

        const handleMouseMove = (e) => {
            setGhostPos({ x: e.clientX - 30, y: e.clientY - 30 });
        };

        const handleMouseUp = (e) => {
            setIsDragging(false);
            setGhostPiece(null);

            const el = document.elementFromPoint(e.clientX, e.clientY);
            const sq = el?.closest('[data-row]');
            if (sq && dragFrom) {
                const tr = parseInt(sq.dataset.row);
                const tc = parseInt(sq.dataset.col);
                const isLegal = legalTargets.some(m => m.to[0] === tr && m.to[1] === tc);
                if (isLegal) {
                    onMove?.(dragFrom[0], dragFrom[1], tr, tc);
                    setLastMove({ from: dragFrom, to: [tr, tc] });
                }
            }
            setSelectedSquare(null);
            setLegalTargets([]);
            setDragFrom(null);
        };

        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
        return () => {
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
        };
    }, [isDragging, dragFrom, legalTargets, onMove]);

    const triggerShake = () => {
        setShaking(true);
        setTimeout(() => setShaking(false), 300);
    };

    // Render squares
    const renderSquares = () => {
        const elements = [];
        for (let i = 0; i < 8; i++) {
            for (let j = 0; j < 8; j++) {
                const row = flipped ? 7 - i : i;
                const col = flipped ? 7 - j : j;
                const { isLight, piece, isSelected, isLegalTarget, isLastMove, isCheck, hasPiece } = getSquareInfo(row, col);

                const classNames = [
                    'square',
                    isLight ? 'light' : 'dark',
                    isSelected && 'selected',
                    isLastMove && 'last-move',
                    isCheck && 'in-check',
                    isLegalTarget && 'legal-target',
                ].filter(Boolean).join(' ');

                elements.push(
                    <div
                        key={`${row}-${col}`}
                        className={classNames}
                        data-row={row}
                        data-col={col}
                        onClick={() => handleSquareClick(row, col)}
                        onMouseDown={(e) => handleMouseDown(e, row, col)}
                    >
                        {piece && (
                            <span
                                className={`piece ${piece.color}-piece`}
                                style={{ opacity: isDragging && dragFrom?.[0] === row && dragFrom?.[1] === col ? 0.3 : 1 }}
                            >
                                {PIECE_UNICODE[piece.color]?.[piece.type]}
                            </span>
                        )}
                        {isLegalTarget && !hasPiece && <div className="legal-dot" />}
                        {isLegalTarget && hasPiece && <div className="legal-capture-ring" />}
                    </div>
                );
            }
        }
        return elements;
    };

    const rankLabels = Array.from({ length: 8 }, (_, i) => {
        const r = flipped ? 7 - i : i;
        return <div key={r} className="rank-label">{RANKS[r]}</div>;
    });

    const fileLabels = Array.from({ length: 8 }, (_, i) => {
        const c = flipped ? 7 - i : i;
        return <div key={c} className="file-label">{FILES[c]}</div>;
    });

    return (
        <>
            <div className="board-wrapper">
                <div className="rank-labels">{rankLabels}</div>
                <div ref={boardRef} className={`chessboard${shaking ? ' shake' : ''}`}>
                    {renderSquares()}
                </div>
            </div>
            <div className="file-labels" style={{ marginLeft: 20 }}>{fileLabels}</div>

            {/* Drag ghost */}
            {isDragging && ghostPiece && (
                <div
                    className="piece-ghost"
                    style={{ left: ghostPos.x, top: ghostPos.y }}
                >
                    {PIECE_UNICODE[ghostPiece.color]?.[ghostPiece.type]}
                </div>
            )}
        </>
    );
}

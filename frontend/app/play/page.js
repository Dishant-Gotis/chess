'use client';

import { useState, useEffect, useCallback } from 'react';
import styles from './page.module.css';
import ChessBoard from '../components/ChessBoard';
import { PlayerCard, MoveHistory } from '../components/Panels';
import { NewGameModal, PromotionModal, GameOverModal } from '../components/Modals';
import { api } from '../lib/api';
import { sounds } from '../lib/sounds';

export default function Home() {
    const [state, setState] = useState(null);
    const [showNewGame, setShowNewGame] = useState(true);
    const [showPromotion, setShowPromotion] = useState(false);
    const [showGameOver, setShowGameOver] = useState(false);
    const [gameOverInfo, setGameOverInfo] = useState({ title: '', reason: '' });
    const [promotionData, setPromotionData] = useState(null);
    const [flipped, setFlipped] = useState(false);
    const [soundEnabled, setSoundEnabled] = useState(true);
    const [thinking, setThinking] = useState(false);
    const [statusText, setStatusText] = useState('White to move');

    useEffect(() => {
        api.getState().then(data => {
            setState(data);
            updateStatusText(data);
        }).catch(() => {
            setStatusText('⚠ Cannot connect to server. Start the Python backend first.');
        });
    }, []);

    const updateStatusText = useCallback((data) => {
        if (!data) return;
        const s = data.status;
        if (s.status === 'checkmate') setStatusText(s.reason);
        else if (s.status === 'stalemate' || s.status === 'draw') setStatusText(s.reason);
        else if (s.status === 'resigned') setStatusText(s.reason);
        else if (s.inCheck) setStatusText(`Check! ${capitalize(data.activeColor)} to move`);
        else setStatusText(`${capitalize(data.activeColor)} to move`);
    }, []);

    const handleNewGame = async (settings) => {
        setShowNewGame(false);
        setShowGameOver(false);
        setThinking(true);
        setStatusText('Starting new game...');

        try {
            const data = await api.newGame(settings.mode, settings.aiColor, settings.difficulty);
            setState(data);
            updateStatusText(data);

            if (settings.mode === 'ai' && settings.aiColor === 'white') {
                setFlipped(true);
            } else {
                setFlipped(false);
            }
        } catch (err) {
            setStatusText('Error starting game. Is the server running?');
        }
        setThinking(false);
    };

    const handleMove = useCallback(async (fr, fc, tr, tc) => {
        if (!state || state.gameOver) return;

        const key = `${fr},${fc}`;
        const moves = state.legalMoves[key] || [];
        const targetMoves = moves.filter(m => m.to[0] === tr && m.to[1] === tc);
        const isPromotion = targetMoves.some(m => m.promotion);

        if (isPromotion) {
            setPromotionData({ fr, fc, tr, tc });
            setShowPromotion(true);
            return;
        }

        await executeMove(fr, fc, tr, tc, null);
    }, [state]);

    const handlePromotion = async (piece) => {
        setShowPromotion(false);
        if (promotionData) {
            const { fr, fc, tr, tc } = promotionData;
            await executeMove(fr, fc, tr, tc, piece);
            setPromotionData(null);
        }
    };

    const executeMove = async (fr, fc, tr, tc, promotion) => {
        try {
            setThinking(true);
            const data = await api.makeMove(fr, fc, tr, tc, promotion);

            if (data.playerMove?.success === false) {
                sounds.illegal();
                setThinking(false);
                return;
            }

            // 1) Show the player's move immediately
            if (data.playerMove?.success) {
                playMoveSound(data.playerMove);

                // If there's an AI move coming, show intermediate state first
                if (data.aiMove?.success) {
                    // Apply player-move state (board after player moved, before AI)
                    const playerState = {
                        ...data.state,
                        board: data.playerMove.board,
                        moveList: data.playerMove.moveList,
                        capturedPieces: data.playerMove.capturedPieces,
                        activeColor: data.playerMove.status?.inCheck ? data.state.activeColor : (fr === undefined ? data.state.activeColor : (data.playerMove.board ? data.state.aiColor : data.state.activeColor)),
                        legalMoves: {},  // Disable interaction while AI thinks
                    };
                    // Use the moveList from playerMove if available, otherwise strip AI's last move
                    const movesSoFar = data.state.moveList ? data.state.moveList.slice(0, -1) : data.playerMove.moveList || [];
                    setState(prev => ({
                        ...data.state,
                        board: data.playerMove.board || data.state.board,
                        moveList: movesSoFar,
                        capturedPieces: data.playerMove.capturedPieces || data.state.capturedPieces,
                        legalMoves: {},
                    }));
                    setStatusText('AI is thinking...');

                    // 2) Wait, then show AI's move
                    await new Promise(resolve => setTimeout(resolve, 800));

                    playMoveSound(data.aiMove);
                    setState(data.state);
                    updateStatusText(data.state);

                    if (data.state.status?.status !== 'playing') {
                        handleGameOverEvent(data.state.status);
                    }
                } else {
                    // No AI move — just apply final state
                    setState(data.state);
                    updateStatusText(data.state);

                    if (data.state.status?.status !== 'playing') {
                        handleGameOverEvent(data.state.status);
                    }
                }
            }
        } catch (err) {
            console.error('Move error:', err);
        }
        setThinking(false);
    };

    const playMoveSound = (moveData) => {
        if (!moveData) return;
        const san = moveData.san || '';
        const s = moveData.status || {};
        if (s.status === 'checkmate') sounds.gameOver();
        else if (san.includes('+')) sounds.check();
        else if (san.includes('O-O')) sounds.castle();
        else if (san.includes('x')) sounds.capture();
        else sounds.move();
    };

    const handleGameOverEvent = (status) => {
        let title = 'Game Over';
        if (status.status === 'checkmate') title = '♚ Checkmate!';
        else if (status.status === 'stalemate') title = '½ Stalemate';
        else if (status.status === 'draw') title = '½ Draw';
        else if (status.status === 'resigned') title = '🏳️ Resigned';
        sounds.gameOver();
        setGameOverInfo({ title, reason: status.reason || 'The game has ended.' });
        setTimeout(() => setShowGameOver(true), 500);
    };

    const handleUndo = async () => {
        try {
            const data = await api.undo();
            if (data.success) { setState(data.state); updateStatusText(data.state); }
        } catch (err) { console.error('Undo error:', err); }
    };

    const handleResign = async () => {
        if (!state || state.gameOver) return;
        if (!confirm('Are you sure you want to resign?')) return;
        try {
            const data = await api.resign();
            setState(data);
            updateStatusText(data);
            handleGameOverEvent(data.status);
        } catch (err) { console.error('Resign error:', err); }
    };

    const toggleSound = () => {
        const enabled = sounds.toggle();
        setSoundEnabled(enabled);
    };

    const capitalize = (s) => s ? s.charAt(0).toUpperCase() + s.slice(1) : '';

    const blackName = state?.mode === 'ai' && state?.aiColor === 'black' ? '🤖 AI' : 'Player 2';
    const whiteName = state?.mode === 'ai' && state?.aiColor === 'white' ? '🤖 AI' : 'Player 1';

    return (
        <div className={styles.app}>
            {/* Header */}
            <header className={styles.header}>
                <div className={styles.logo}>
                    ♔ <span className={styles.logoText}>Chess</span>
                </div>
                <div className={styles.headerRight}>
                    <button className={styles.iconBtn} onClick={toggleSound} title="Toggle Sound">
                        {soundEnabled ? '🔊' : '🔇'}
                    </button>
                    <button className={styles.newGameBtn} onClick={() => setShowNewGame(true)}>
                        New Game
                    </button>
                </div>
            </header>

            {/* Main Game Area */}
            <main className={styles.gameArea}>
                {/* Left Panel — Black */}
                <aside className="side-panel">
                    <PlayerCard
                        color="black"
                        name={blackName}
                        label="Black pieces"
                        active={state?.activeColor === 'black'}
                        capturedPieces={state?.capturedPieces?.white || []}
                    />
                </aside>

                {/* Board */}
                <section className={styles.boardSection}>
                    <ChessBoard
                        boardData={state?.board}
                        legalMoves={state?.legalMoves || {}}
                        activeColor={state?.activeColor}
                        status={state?.status}
                        flipped={flipped}
                        onMove={handleMove}
                        disabled={thinking || state?.gameOver}
                    />
                    <div className={styles.gameControls}>
                        <button className={styles.ctrlBtn} onClick={() => setFlipped(f => !f)} title="Flip Board">🔄</button>
                        <button className={styles.ctrlBtn} onClick={handleUndo} title="Undo Move">↩️</button>
                        <button className={styles.ctrlBtn} onClick={handleResign} title="Resign">🏳️</button>
                    </div>
                </section>

                {/* Right Panel — White + Move History */}
                <aside className="side-panel">
                    <PlayerCard
                        color="white"
                        name={whiteName}
                        label="White pieces"
                        active={state?.activeColor === 'white'}
                        capturedPieces={state?.capturedPieces?.black || []}
                    />
                    <MoveHistory moves={state?.moveList || []} />
                </aside>
            </main>

            {/* Status Bar */}
            <div className={`${styles.statusBar}${state?.status?.inCheck ? ` ${styles.inCheck}` : ''}${thinking ? ` ${styles.thinking}` : ''}`}>
                {statusText}
            </div>

            {/* Modals */}
            <NewGameModal
                isOpen={showNewGame}
                onClose={() => setShowNewGame(false)}
                onStart={handleNewGame}
            />

            <PromotionModal
                isOpen={showPromotion}
                color={state?.activeColor || 'white'}
                onSelect={handlePromotion}
            />

            <GameOverModal
                isOpen={showGameOver}
                title={gameOverInfo.title}
                reason={gameOverInfo.reason}
                onPlayAgain={() => { setShowGameOver(false); setShowNewGame(true); }}
                onClose={() => setShowGameOver(false)}
            />
        </div>
    );
}

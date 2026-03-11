'use client';

import { useEffect, useRef } from 'react';
import Link from 'next/link';
import styles from './page.module.css';

const FLOATING_PIECES = ['♔', '♛', '♜', '♝', '♞', '♟', '♚', '♕', '♖', '♗', '♘', '♙'];

function FloatingPiece({ piece, index }) {
    const style = {
        '--delay': `${index * 0.7}s`,
        '--duration': `${15 + (index % 5) * 3}s`,
        '--x-start': `${5 + (index * 8) % 90}%`,
        '--y-offset': `${(index % 3) * 30}px`,
        '--size': `${28 + (index % 4) * 12}px`,
        '--opacity': `${0.04 + (index % 3) * 0.02}`,
    };

    return <span className={styles.floatingPiece} style={style}>{piece}</span>;
}

export default function LandingPage() {
    return (
        <div className={styles.landing}>
            {/* Floating background pieces */}
            <div className={styles.floatingBg} aria-hidden="true">
                {FLOATING_PIECES.map((p, i) => (
                    <FloatingPiece key={i} piece={p} index={i} />
                ))}
            </div>

            {/* Navigation */}
            <nav className={styles.nav}>
                <div className={styles.navLogo}>
                    ♔ <span className={styles.navLogoText}>Chess</span>
                </div>
                <Link href="/play" className={styles.navCta}>
                    Play Now
                </Link>
            </nav>

            {/* Hero */}
            <section className={styles.hero}>
                <div className={styles.heroContent}>
                    <div className={styles.heroBadge}>Free &bull; Open Source &bull; No Sign-up</div>
                    <h1 className={styles.heroTitle}>
                        Master the Game of <span className={styles.heroAccent}>Kings</span>
                    </h1>
                    <p className={styles.heroSubtitle}>
                        Experience chess like never before. Play against a challenging AI or
                        go head-to-head with a friend — all in a beautifully crafted, premium interface.
                    </p>
                    <div className={styles.heroCtas}>
                        <Link href="/play" className={styles.ctaPrimary}>
                            <span className={styles.ctaIcon}>♔</span> Start Playing
                        </Link>
                        <Link href="/play" className={styles.ctaSecondary}>
                            vs AI Challenge
                        </Link>
                    </div>
                </div>
                <div className={styles.heroVisual}>
                    <div className={styles.boardPreview}>
                        <div className={styles.miniBoard}>
                            {Array.from({ length: 64 }, (_, i) => {
                                const row = Math.floor(i / 8);
                                const col = i % 8;
                                const isLight = (row + col) % 2 === 0;
                                const pieces = {
                                    '0,0': '♜', '0,1': '♞', '0,2': '♝', '0,3': '♛',
                                    '0,4': '♚', '0,5': '♝', '0,6': '♞', '0,7': '♜',
                                    '1,0': '♟', '1,1': '♟', '1,2': '♟', '1,3': '♟',
                                    '1,4': '♟', '1,5': '♟', '1,6': '♟', '1,7': '♟',
                                    '6,0': '♙', '6,1': '♙', '6,2': '♙', '6,3': '♙',
                                    '6,4': '♙', '6,5': '♙', '6,6': '♙', '6,7': '♙',
                                    '7,0': '♖', '7,1': '♘', '7,2': '♗', '7,3': '♕',
                                    '7,4': '♔', '7,5': '♗', '7,6': '♘', '7,7': '♖',
                                };
                                const piece = pieces[`${row},${col}`];
                                const isBlack = row <= 1;

                                return (
                                    <div key={i} className={`${styles.miniSquare} ${isLight ? styles.miniLight : styles.miniDark}`}>
                                        {piece && (
                                            <span className={isBlack ? styles.miniBlackPiece : styles.miniWhitePiece}>
                                                {piece}
                                            </span>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                        <div className={styles.boardGlow}></div>
                    </div>
                </div>
            </section>

            {/* Features */}
            <section className={styles.features}>
                <h2 className={styles.sectionTitle}>Why You&apos;ll Love It</h2>
                <div className={styles.featureGrid}>
                    {[
                        {
                            icon: '🤖',
                            title: 'Smart AI Opponent',
                            desc: 'Three difficulty levels powered by minimax with alpha-beta pruning. From casual to seriously tough.',
                        },
                        {
                            icon: '🎨',
                            title: 'Premium Design',
                            desc: 'Dark theme with glassmorphism, smooth animations, and a polished interface that feels professional.',
                        },
                        {
                            icon: '👆',
                            title: 'Click or Drag',
                            desc: 'Move pieces your way — click-to-move or drag-and-drop, with legal move indicators to guide you.',
                        },
                        {
                            icon: '📜',
                            title: 'Full Move History',
                            desc: 'Every move recorded in standard algebraic notation. Captured pieces tracked in real time.',
                        },
                        {
                            icon: '🔊',
                            title: 'Immersive Sounds',
                            desc: 'Procedurally generated audio for moves, captures, checks, and castles — no downloads needed.',
                        },
                        {
                            icon: '⚡',
                            title: 'Instant & Free',
                            desc: 'No sign-up, no downloads, no ads. Just open and play. Works on desktop and mobile.',
                        },
                    ].map((f, i) => (
                        <div key={i} className={styles.featureCard}>
                            <div className={styles.featureIcon}>{f.icon}</div>
                            <h3 className={styles.featureTitle}>{f.title}</h3>
                            <p className={styles.featureDesc}>{f.desc}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* Game Modes */}
            <section className={styles.modes}>
                <h2 className={styles.sectionTitle}>Choose Your Battle</h2>
                <div className={styles.modeCards}>
                    <div className={styles.modeCard}>
                        <div className={styles.modeEmoji}>👥</div>
                        <h3 className={styles.modeTitle}>Player vs Player</h3>
                        <p className={styles.modeDesc}>
                            Challenge a friend on the same device. Take turns and see who reigns supreme.
                        </p>
                        <Link href="/play" className={styles.modeLink}>
                            Play PvP →
                        </Link>
                    </div>
                    <div className={`${styles.modeCard} ${styles.modeCardFeatured}`}>
                        <div className={styles.modeBadge}>Popular</div>
                        <div className={styles.modeEmoji}>🤖</div>
                        <h3 className={styles.modeTitle}>Player vs AI</h3>
                        <p className={styles.modeDesc}>
                            Test your skills against three difficulty levels. Can you beat the engine on hard?
                        </p>
                        <Link href="/play" className={styles.modeLinkPrimary}>
                            Challenge AI →
                        </Link>
                    </div>
                </div>
            </section>

            {/* CTA */}
            <section className={styles.finalCta}>
                <h2 className={styles.ctaTitle}>Ready to Play?</h2>
                <p className={styles.ctaSubtitle}>No account needed. Jump in and make your first move.</p>
                <Link href="/play" className={styles.ctaPrimary}>
                    <span className={styles.ctaIcon}>♔</span> Let&apos;s Go
                </Link>
            </section>

            {/* Footer */}
            <footer className={styles.footer}>
                <div className={styles.footerContent}>
                    <span>♔ Chess</span>
                    <span className={styles.footerDot}>·</span>
                    <span>Built with Next.js + Python</span>
                    <span className={styles.footerDot}>·</span>
                    <span>Open Source</span>
                </div>
            </footer>
        </div>
    );
}

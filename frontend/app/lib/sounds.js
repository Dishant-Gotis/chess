/**
 * Procedural sound effects using Web Audio API
 */

let ctx = null;
let enabled = true;

function getCtx() {
    if (!ctx && typeof window !== 'undefined') {
        ctx = new (window.AudioContext || window.webkitAudioContext)();
    }
    return ctx;
}

function playTone(freq, duration, type = 'sine', volume = 0.15) {
    if (!enabled) return;
    try {
        const c = getCtx();
        if (!c) return;
        const osc = c.createOscillator();
        const gain = c.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(freq, c.currentTime);
        gain.gain.setValueAtTime(volume, c.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, c.currentTime + duration);
        osc.connect(gain);
        gain.connect(c.destination);
        osc.start(c.currentTime);
        osc.stop(c.currentTime + duration);
    } catch (e) { /* ignore */ }
}

function playNoise(duration, volume = 0.05) {
    if (!enabled) return;
    try {
        const c = getCtx();
        if (!c) return;
        const bufferSize = c.sampleRate * duration;
        const buffer = c.createBuffer(1, bufferSize, c.sampleRate);
        const data = buffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) data[i] = Math.random() * 2 - 1;
        const source = c.createBufferSource();
        source.buffer = buffer;
        const gain = c.createGain();
        gain.gain.setValueAtTime(volume, c.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, c.currentTime + duration);
        const filter = c.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.value = 800;
        source.connect(filter);
        filter.connect(gain);
        gain.connect(c.destination);
        source.start(c.currentTime);
    } catch (e) { /* ignore */ }
}

export const sounds = {
    move()    { playTone(440, 0.08, 'sine', 0.12); playNoise(0.05, 0.03); },
    capture() { playTone(300, 0.12, 'triangle', 0.18); playNoise(0.1, 0.06); },
    check()   { playTone(660, 0.08, 'square', 0.1); setTimeout(() => playTone(880, 0.1, 'square', 0.08), 100); },
    castle()  { playTone(350, 0.06, 'sine', 0.1); setTimeout(() => playTone(440, 0.08, 'sine', 0.1), 80); },
    gameOver(){ playTone(440, 0.2, 'sine', 0.12); setTimeout(() => playTone(330, 0.3, 'sine', 0.1), 200); },
    illegal() { playTone(200, 0.15, 'sawtooth', 0.08); },
    toggle()  { enabled = !enabled; return enabled; },
    isEnabled() { return enabled; },
};

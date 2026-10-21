/**
 * O.M.N.I.S. Core Visualizer Engine
 * 1. Arc Reactor Canvas: Multi-ring gyro, particle vortex, and energy core
 * 2. Waveform Canvas: Real-time Audio Spectrum & Waveform Equalizer
 */

class ArcReactorVisualizer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        
        // System state: 'STANDBY', 'LISTENING', 'COMPUTING', 'SPEAKING'
        this.state = 'STANDBY';
        this.angle1 = 0;
        this.angle2 = 0;
        this.angle3 = 0;
        this.pulse = 0;
        this.pulseSpeed = 0.04;

        // Particle System
        this.particles = [];
        this.initParticles(36);

        this.animate = this.animate.bind(this);
        requestAnimationFrame(this.animate);
    }

    setState(newState) {
        this.state = newState;
        if (newState === 'LISTENING') {
            this.pulseSpeed = 0.12;
        } else if (newState === 'COMPUTING') {
            this.pulseSpeed = 0.08;
        } else if (newState === 'SPEAKING') {
            this.pulseSpeed = 0.09;
        } else {
            this.pulseSpeed = 0.04;
        }
    }

    initParticles(count) {
        this.particles = [];
        for (let i = 0; i < count; i++) {
            this.particles.push({
                angle: Math.random() * Math.PI * 2,
                radius: 40 + Math.random() * 90,
                speed: 0.005 + Math.random() * 0.02,
                size: 1 + Math.random() * 2.2,
                alpha: 0.2 + Math.random() * 0.8
            });
        }
    }

    animate() {
        if (!this.canvas || !this.ctx) return;
        const ctx = this.ctx;
        const width = this.canvas.width;
        const height = this.canvas.height;
        const cx = width / 2;
        const cy = height / 2;

        ctx.clearRect(0, 0, width, height);

        // Speeds adjusted per state
        let spinMultiplier = 1;
        let mainColor = '#00f0ff';
        let glowColor = 'rgba(0, 240, 255, 0.45)';

        if (this.state === 'LISTENING') {
            spinMultiplier = 2.4;
            mainColor = '#ff007f';
            glowColor = 'rgba(255, 0, 127, 0.5)';
        } else if (this.state === 'COMPUTING') {
            spinMultiplier = 1.8;
            mainColor = '#9d4edd';
            glowColor = 'rgba(157, 78, 221, 0.5)';
        } else if (this.state === 'SPEAKING') {
            spinMultiplier = 1.5;
            mainColor = '#00ffaa';
            glowColor = 'rgba(0, 255, 170, 0.5)';
        }

        this.angle1 += 0.008 * spinMultiplier;
        this.angle2 -= 0.012 * spinMultiplier;
        this.angle3 += 0.018 * spinMultiplier;
        this.pulse += this.pulseSpeed;

        const pulseScale = 1 + Math.sin(this.pulse) * 0.06;

        // 1. Outer Glow Aura
        const aura = ctx.createRadialGradient(cx, cy, 30, cx, cy, 170 * pulseScale);
        aura.addColorStop(0, glowColor);
        aura.addColorStop(0.7, 'rgba(0, 0, 0, 0.1)');
        aura.addColorStop(1, 'transparent');
        ctx.fillStyle = aura;
        ctx.beginPath();
        ctx.arc(cx, cy, 170 * pulseScale, 0, Math.PI * 2);
        ctx.fill();

        // 2. Outer Technical Graduation Ring (Fixed with ticks)
        ctx.save();
        ctx.translate(cx, cy);
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(0, 0, 155, 0, Math.PI * 2);
        ctx.stroke();

        for (let i = 0; i < 72; i++) {
            const rad = (i * Math.PI * 2) / 72;
            const innerR = (i % 6 === 0) ? 144 : 149;
            ctx.beginPath();
            ctx.moveTo(Math.cos(rad) * innerR, Math.sin(rad) * innerR);
            ctx.lineTo(Math.cos(rad) * 155, Math.sin(rad) * 155);
            ctx.strokeStyle = (i % 6 === 0) ? mainColor : 'rgba(255, 255, 255, 0.15)';
            ctx.lineWidth = (i % 6 === 0) ? 2 : 1;
            ctx.stroke();
        }
        ctx.restore();

        // 3. Middle Segmented Rotating Gyro Ring (Clockwise)
        ctx.save();
        ctx.translate(cx, cy);
        ctx.rotate(this.angle1);
        ctx.strokeStyle = mainColor;
        ctx.lineWidth = 3;
        ctx.shadowColor = mainColor;
        ctx.shadowBlur = 12;

        const segments = 4;
        const segAngle = (Math.PI * 2) / segments;
        for (let i = 0; i < segments; i++) {
            ctx.beginPath();
            ctx.arc(0, 0, 125 * pulseScale, i * segAngle, i * segAngle + segAngle * 0.7);
            ctx.stroke();

            // Accent Notch
            const tipAngle = i * segAngle + segAngle * 0.7;
            ctx.beginPath();
            ctx.arc(Math.cos(tipAngle) * 125 * pulseScale, Math.sin(tipAngle) * 125 * pulseScale, 4, 0, Math.PI * 2);
            ctx.fillStyle = '#fff';
            ctx.fill();
        }
        ctx.restore();

        // 4. Inner Reverse Rotating Tech Circuit (Counter-Clockwise)
        ctx.save();
        ctx.translate(cx, cy);
        ctx.rotate(this.angle2);
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.35)';
        ctx.lineWidth = 1.5;
        ctx.shadowBlur = 6;
        ctx.shadowColor = mainColor;

        const innerSegs = 6;
        const innerSegAngle = (Math.PI * 2) / innerSegs;
        for (let i = 0; i < innerSegs; i++) {
            ctx.beginPath();
            ctx.arc(0, 0, 88 * pulseScale, i * innerSegAngle, i * innerSegAngle + innerSegAngle * 0.55);
            ctx.stroke();
        }
        ctx.restore();

        // 5. Orbiting Quantum Particles
        ctx.save();
        ctx.translate(cx, cy);
        this.particles.forEach(p => {
            p.angle += p.speed * spinMultiplier;
            const px = Math.cos(p.angle) * p.radius * pulseScale;
            const py = Math.sin(p.angle) * p.radius * pulseScale;

            ctx.beginPath();
            ctx.arc(px, py, p.size, 0, Math.PI * 2);
            ctx.fillStyle = mainColor;
            ctx.globalAlpha = p.alpha;
            ctx.shadowBlur = 8;
            ctx.shadowColor = mainColor;
            ctx.fill();
        });
        ctx.restore();

        // 6. Central Holographic Core
        ctx.save();
        ctx.translate(cx, cy);
        const coreGradient = ctx.createRadialGradient(0, 0, 5, 0, 0, 50 * pulseScale);
        coreGradient.addColorStop(0, '#ffffff');
        coreGradient.addColorStop(0.3, mainColor);
        coreGradient.addColorStop(0.75, glowColor);
        coreGradient.addColorStop(1, 'transparent');

        ctx.fillStyle = coreGradient;
        ctx.beginPath();
        ctx.arc(0, 0, 50 * pulseScale, 0, Math.PI * 2);
        ctx.fill();

        // Central Mini Pulsing Ring
        ctx.rotate(this.angle3);
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 2;
        ctx.shadowBlur = 15;
        ctx.shadowColor = mainColor;
        ctx.beginPath();
        ctx.arc(0, 0, 24 * pulseScale, 0, Math.PI * 2);
        ctx.stroke();

        // Triangle Core Marker
        ctx.beginPath();
        for (let i = 0; i < 3; i++) {
            const rad = (i * Math.PI * 2) / 3;
            const x = Math.cos(rad) * 16 * pulseScale;
            const y = Math.sin(rad) * 16 * pulseScale;
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.closePath();
        ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
        ctx.fill();

        ctx.restore();

        requestAnimationFrame(this.animate);
    }
}


class AudioWaveformVisualizer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        
        this.analyser = null;
        this.audioData = new Uint8Array(64);
        this.isLive = false;
        this.phase = 0;
        this.state = 'STANDBY';

        this.animate = this.animate.bind(this);
        requestAnimationFrame(this.animate);
    }

    setAnalyser(analyserNode) {
        this.analyser = analyserNode;
        this.isLive = true;
        this.audioData = new Uint8Array(this.analyser.frequencyBinCount);
    }

    setState(newState) {
        this.state = newState;
    }

    animate() {
        if (!this.canvas || !this.ctx) return;
        const ctx = this.ctx;
        const width = this.canvas.width;
        const height = this.canvas.height;
        const midY = height / 2;

        ctx.clearRect(0, 0, width, height);

        const barCount = 42;
        const barWidth = 6;
        const barGap = 4;
        const totalWidth = barCount * (barWidth + barGap);
        const startX = (width - totalWidth) / 2;

        let accentColor = '#00f0ff';
        let glowColor = 'rgba(0, 240, 255, 0.5)';

        if (this.state === 'LISTENING') {
            accentColor = '#ff007f';
            glowColor = 'rgba(255, 0, 127, 0.6)';
        } else if (this.state === 'SPEAKING') {
            accentColor = '#00ffaa';
            glowColor = 'rgba(0, 255, 170, 0.5)';
        }

        this.phase += 0.06;

        // If live analyser connected
        if (this.analyser && this.isLive) {
            this.analyser.getByteFrequencyData(this.audioData);
        }

        for (let i = 0; i < barCount; i++) {
            let magnitude = 0;

            if (this.analyser && this.isLive) {
                const dataIndex = Math.floor((i / barCount) * (this.audioData.length / 2));
                magnitude = (this.audioData[dataIndex] / 255) * (height * 0.85);
            } else {
                // Procedural cyberpunk wave modulation
                const distFromCenter = Math.abs(i - barCount / 2) / (barCount / 2);
                const bellCurve = Math.cos(distFromCenter * (Math.PI / 2));
                
                let baseAmp = 8;
                if (this.state === 'LISTENING') baseAmp = 28;
                else if (this.state === 'SPEAKING') baseAmp = 34;

                const wave1 = Math.sin(this.phase + i * 0.28);
                const wave2 = Math.cos(this.phase * 1.4 + i * 0.18);
                magnitude = (Math.abs(wave1 + wave2) * baseAmp * bellCurve) + 4;
            }

            magnitude = Math.max(magnitude, 4);

            const x = startX + i * (barWidth + barGap);
            const topY = midY - magnitude / 2;

            // Draw Mirror Equalizer Bar
            ctx.save();
            const grad = ctx.createLinearGradient(x, topY, x, topY + magnitude);
            grad.addColorStop(0, accentColor);
            grad.addColorStop(0.5, '#ffffff');
            grad.addColorStop(1, accentColor);

            ctx.fillStyle = grad;
            ctx.shadowColor = glowColor;
            ctx.shadowBlur = 8;

            ctx.beginPath();
            ctx.roundRect(x, topY, barWidth, magnitude, 3);
            ctx.fill();

            // Tip Accent Dot
            ctx.fillStyle = '#fff';
            ctx.beginPath();
            ctx.arc(x + barWidth / 2, topY - 3, 1.5, 0, Math.PI * 2);
            ctx.arc(x + barWidth / 2, topY + magnitude + 3, 1.5, 0, Math.PI * 2);
            ctx.fill();

            ctx.restore();
        }

        requestAnimationFrame(this.animate);
    }
}

// Global visualizer instances
window.omnisVisualizer = {
    reactor: null,
    waveform: null,
    init: function() {
        this.reactor = new ArcReactorVisualizer('reactorCanvas');
        this.waveform = new AudioWaveformVisualizer('waveformCanvas');
    },
    setState: function(state) {
        if (this.reactor) this.reactor.setState(state);
        if (this.waveform) this.waveform.setState(state);
    }
};

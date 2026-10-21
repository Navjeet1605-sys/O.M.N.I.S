/**
 * O.M.N.I.S. Core Application Controller
 * Handles Speech-to-Text, Backend API integration, HUD animations, and User Directives.
 */

class OmnisApp {
    constructor() {
        // State
        this.isRecording = false;
        this.voiceEnabled = true;
        this.sfxEnabled = true;
        this.recognition = null;
        this.currentAssistantName = "OMNIS";
        this.currentUserName = "Sir";
        this.speechLang = "en-US";
        this.voiceEngine = "edge";
        this.activeTab = "chatTab";
        this.lastQueryTime = Date.now();

        // Audio Stream Analyser
        this.mediaStream = null;
        this.audioContext = null;
        this.analyser = null;

        // DOM Elements
        this.dom = {
            micBtn: document.getElementById('micButton'),
            micHint: document.getElementById('micHint'),
            inlineMicBtn: document.getElementById('inlineMicBtn'),
            promptForm: document.getElementById('promptForm'),
            promptInput: document.getElementById('promptInput'),
            sendBtn: document.getElementById('sendBtn'),
            liveTranscript: document.getElementById('liveTranscript'),
            chatStream: document.getElementById('chatStream'),
            messageCount: document.getElementById('messageCount'),
            coreStateIndicator: document.getElementById('coreStateIndicator'),
            engineStateBadge: document.getElementById('engineStateBadge'),
            speechStateBadge: document.getElementById('speechStateBadge'),
            systemStatusLabel: document.getElementById('systemStatusLabel'),
            lastDecisionText: document.getElementById('lastDecisionText'),
            hudClock: document.getElementById('hudClock'),
            latencyDisplay: document.getElementById('latencyDisplay'),
            cpuVal: document.getElementById('cpuVal'),
            cpuBar: document.getElementById('cpuBar'),
            memVal: document.getElementById('memVal'),
            memBar: document.getElementById('memBar'),
            sfxToggleBtn: document.getElementById('sfxToggleBtn'),
            voiceToggleBtn: document.getElementById('voiceToggleBtn'),
            settingsBtn: document.getElementById('settingsBtn'),
            settingsModal: document.getElementById('settingsModal'),
            closeSettingsBtn: document.getElementById('closeSettingsBtn'),
            saveConfigBtn: document.getElementById('saveConfigBtn'),
            clearChatBtn: document.getElementById('clearChatBtn'),
            exportChatBtn: document.getElementById('exportChatBtn'),
            refreshGalleryBtn: document.getElementById('refreshGalleryBtn'),
            galleryGrid: document.getElementById('galleryGrid'),
            imageLightboxModal: document.getElementById('imageLightboxModal'),
            lightboxImage: document.getElementById('lightboxImage'),
            lightboxCaption: document.getElementById('lightboxCaption'),
            closeLightboxBtn: document.getElementById('closeLightboxBtn')
        };

        this.init();
    }

    init() {
        // Initialize visualizers
        if (window.omnisVisualizer) {
            window.omnisVisualizer.init();
        }

        // Setup clock
        this.updateClock();
        setInterval(() => this.updateClock(), 1000);

        // Setup Speech Recognition
        this.setupSpeechRecognition();

        // Bind event listeners
        this.bindEvents();

        // Initial Backend sync
        this.fetchTelemetry();
        this.fetchChatLog();
        this.fetchGallery();

        // Regular telemetry polling
        setInterval(() => this.fetchTelemetry(), 4000);
    }

    updateClock() {
        const now = new Date();
        const timeStr = now.toTimeString().split(' ')[0];
        if (this.dom.hudClock) {
            this.dom.hudClock.textContent = timeStr;
        }
    }

    // ================== SPEECH RECOGNITION ==================

    setupSpeechRecognition() {
        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRec) {
            console.warn("Speech Recognition API not supported in this browser.");
            if (this.dom.micHint) {
                this.dom.micHint.textContent = "SPEECH REC UNAVAILABLE (TYPE BELOW)";
            }
            return;
        }

        this.recognition = new SpeechRec();
        this.recognition.lang = this.speechLang;
        this.recognition.continuous = false;
        this.recognition.interimResults = true;

        this.recognition.onstart = () => {
            this.isRecording = true;
            this.updateSystemState('LISTENING');
            if (this.dom.micBtn) this.dom.micBtn.classList.add('recording');
            if (this.dom.speechStateBadge) {
                this.dom.speechStateBadge.textContent = "MIC: LISTENING...";
                this.dom.speechStateBadge.className = "speech-recording";
            }
            if (this.dom.micHint) this.dom.micHint.textContent = "LISTENING... SPEAK DIRECTIVE";
            if (window.omnisSFX) window.omnisSFX.playMicOn();

            // Connect real audio analyser for waveform
            this.startMicAudioStream();
        };

        this.recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }

            const currentText = finalTranscript || interimTranscript;
            if (currentText && this.dom.liveTranscript) {
                this.dom.liveTranscript.textContent = `"${currentText}"`;
            }

            if (finalTranscript) {
                if (this.dom.promptInput) {
                    this.dom.promptInput.value = finalTranscript;
                }
                this.stopSpeechRecognition();
                this.handlePromptSubmit(finalTranscript);
            }
        };

        this.recognition.onerror = (event) => {
            console.error("Speech Recognition Error:", event.error);
            this.stopSpeechRecognition();
            if (this.dom.liveTranscript) {
                this.dom.liveTranscript.textContent = `Acoustic sensor notice: ${event.error}. Press Arc Mic to retry.`;
            }
        };

        this.recognition.onend = () => {
            this.stopSpeechRecognition();
        };
    }

    async startMicAudioStream() {
        try {
            if (!this.audioContext) {
                const AudioCtx = window.AudioContext || window.webkitAudioContext;
                if (AudioCtx) this.audioContext = new AudioCtx();
            }
            if (this.audioContext && this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
            }

            if (!this.mediaStream && navigator.mediaDevices) {
                this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
                const source = this.audioContext.createMediaStreamSource(this.mediaStream);
                this.analyser = this.audioContext.createAnalyser();
                this.analyser.fftSize = 128;
                source.connect(this.analyser);

                if (window.omnisVisualizer && window.omnisVisualizer.waveform) {
                    window.omnisVisualizer.waveform.setAnalyser(this.analyser);
                }
            }
        } catch (e) {
            console.log("Mic stream fallback to procedural wave:", e);
        }
    }

    startSpeechRecognition() {
        if (!this.recognition) return;
        try {
            this.recognition.lang = this.speechLang;
            this.recognition.start();
        } catch (e) {
            console.warn("Recognition already active or failed to start:", e);
        }
    }

    stopSpeechRecognition() {
        this.isRecording = false;
        if (this.dom.micBtn) this.dom.micBtn.classList.remove('recording');
        if (this.dom.speechStateBadge) {
            this.dom.speechStateBadge.textContent = "MIC: READY";
            this.dom.speechStateBadge.className = "speech-idle";
        }
        if (this.dom.micHint) this.dom.micHint.textContent = "PRESS SPACE TO TALK";
        this.updateSystemState('STANDBY');

        try {
            if (this.recognition) this.recognition.stop();
        } catch (e) {}

        if (window.omnisSFX) window.omnisSFX.playMicOff();
    }

    toggleSpeechRecognition() {
        if (this.isRecording) {
            this.stopSpeechRecognition();
        } else {
            this.startSpeechRecognition();
        }
    }

    // ================== EVENT BINDINGS ==================

    bindEvents() {
        // Arc Mic button
        if (this.dom.micBtn) {
            this.dom.micBtn.addEventListener('click', () => {
                this.toggleSpeechRecognition();
            });
        }

        // Inline mic button in input frame
        if (this.dom.inlineMicBtn) {
            this.dom.inlineMicBtn.addEventListener('click', () => {
                this.toggleSpeechRecognition();
            });
        }

        // Spacebar push-to-talk
        window.addEventListener('keydown', (e) => {
            // Ignore if user is currently typing in input
            if (document.activeElement === this.dom.promptInput) return;

            if (e.code === 'Space' && !e.repeat) {
                e.preventDefault();
                this.toggleSpeechRecognition();
            }
        });

        // Form submit
        if (this.dom.promptForm) {
            this.dom.promptForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const query = this.dom.promptInput.value.trim();
                if (query) {
                    this.handlePromptSubmit(query);
                    this.dom.promptInput.value = '';
                }
            });
        }

        // Quick Suggestion Chips
        document.querySelectorAll('.chip-item').forEach(chip => {
            chip.addEventListener('click', () => {
                const prompt = chip.getAttribute('data-prompt');
                if (prompt) {
                    if (window.omnisSFX) window.omnisSFX.playTick();
                    this.handlePromptSubmit(prompt);
                }
            });
        });

        // Tactical Automation Buttons
        document.querySelectorAll('.auto-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const cmd = btn.getAttribute('data-cmd');
                if (cmd) {
                    if (window.omnisSFX) window.omnisSFX.playActivate();
                    this.handlePromptSubmit(cmd);
                }
            });
        });

        // Tab Switching
        document.querySelectorAll('.panel-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                const targetId = tab.getAttribute('data-target');
                this.switchTab(targetId, tab);
            });
        });

        // SFX Toggle
        if (this.dom.sfxToggleBtn) {
            this.dom.sfxToggleBtn.addEventListener('click', () => {
                if (window.omnisSFX) {
                    this.sfxEnabled = window.omnisSFX.toggle();
                    this.dom.sfxToggleBtn.style.opacity = this.sfxEnabled ? "1" : "0.4";
                }
            });
        }

        // Voice Output Toggle
        if (this.dom.voiceToggleBtn) {
            this.dom.voiceToggleBtn.addEventListener('click', () => {
                this.voiceEnabled = !this.voiceEnabled;
                this.dom.voiceToggleBtn.style.opacity = this.voiceEnabled ? "1" : "0.4";
                if (window.omnisSFX) window.omnisSFX.playTick();
            });
        }

        // Settings Modal
        if (this.dom.settingsBtn && this.dom.settingsModal) {
            this.dom.settingsBtn.addEventListener('click', () => {
                this.dom.settingsModal.classList.add('open');
                if (window.omnisSFX) window.omnisSFX.playTick();
            });
        }

        if (this.dom.closeSettingsBtn && this.dom.settingsModal) {
            this.dom.closeSettingsBtn.addEventListener('click', () => {
                this.dom.settingsModal.classList.remove('open');
            });
        }

        if (this.dom.saveConfigBtn) {
            this.dom.saveConfigBtn.addEventListener('click', () => {
                this.saveSettings();
                this.dom.settingsModal.classList.remove('open');
            });
        }

        // Clear Chat
        if (this.dom.clearChatBtn) {
            this.dom.clearChatBtn.addEventListener('click', async () => {
                if (confirm("Reset neural chat log history?")) {
                    try {
                        await fetch('/api/clear_chatlog', { method: 'POST' });
                        this.dom.chatStream.innerHTML = '';
                        this.appendChatMessage("OMNIS", "Chat telemetry reset. All neural buffer memory cleared.", ["SYSTEM_RESET"]);
                    } catch (e) {
                        console.error("Failed to clear chat:", e);
                    }
                }
            });
        }

        // Export Chat
        if (this.dom.exportChatBtn) {
            this.dom.exportChatBtn.addEventListener('click', () => {
                this.exportChatHistory();
            });
        }

        // Refresh Gallery
        if (this.dom.refreshGalleryBtn) {
            this.dom.refreshGalleryBtn.addEventListener('click', () => {
                this.fetchGallery();
            });
        }

        // Close Lightbox
        if (this.dom.closeLightboxBtn && this.dom.imageLightboxModal) {
            this.dom.closeLightboxBtn.addEventListener('click', () => {
                this.dom.imageLightboxModal.classList.remove('open');
            });
            this.dom.imageLightboxModal.addEventListener('click', (e) => {
                if (e.target === this.dom.imageLightboxModal) {
                    this.dom.imageLightboxModal.classList.remove('open');
                }
            });
        }
    }

    switchTab(tabId, tabButton) {
        document.querySelectorAll('.panel-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-view').forEach(v => v.classList.remove('active'));

        tabButton.classList.add('active');
        const targetView = document.getElementById(tabId);
        if (targetView) targetView.classList.add('active');
        this.activeTab = tabId;

        if (tabId === 'galleryTab') {
            this.fetchGallery();
        }
        if (window.omnisSFX) window.omnisSFX.playTick();
    }

    // ================== CORE HUD STATE UPDATER ==================

    updateSystemState(state) {
        if (window.omnisVisualizer) {
            window.omnisVisualizer.setState(state);
        }

        if (this.dom.engineStateBadge) {
            this.dom.engineStateBadge.textContent = state;
            if (state === 'LISTENING') {
                this.dom.engineStateBadge.style.borderColor = 'var(--magenta)';
                this.dom.engineStateBadge.style.color = 'var(--magenta)';
            } else if (state === 'COMPUTING') {
                this.dom.engineStateBadge.style.borderColor = 'var(--purple)';
                this.dom.engineStateBadge.style.color = 'var(--purple)';
            } else if (state === 'SPEAKING') {
                this.dom.engineStateBadge.style.borderColor = 'var(--green)';
                this.dom.engineStateBadge.style.color = 'var(--green)';
            } else {
                this.dom.engineStateBadge.style.borderColor = 'var(--cyan)';
                this.dom.engineStateBadge.style.color = 'var(--cyan)';
            }
        }

        if (this.dom.coreStateIndicator) {
            const labels = {
                'STANDBY': 'CORE ENGAGED // ACOUSTIC READY',
                'LISTENING': 'ACOUSTIC RECEPTORS ACTIVE // TRANSCRIBING',
                'COMPUTING': 'DMM PARSING DIRECTIVE // NEURAL REASONING',
                'SPEAKING': 'SYNTHESIZING VOCAL RESPONSE // EMITTING'
            };
            this.dom.coreStateIndicator.textContent = labels[state] || 'CORE ACTIVE';
        }
    }

    // ================== PROMPT PROCESSING ==================

    async handlePromptSubmit(queryText) {
        if (!queryText.trim()) return;

        const startTime = Date.now();
        this.updateSystemState('COMPUTING');

        // Optimistically render User Message
        this.appendChatMessage(this.currentUserName, queryText, ["USER_INPUT"], true);

        if (this.dom.liveTranscript) {
            this.dom.liveTranscript.textContent = `Directive: "${queryText}"`;
        }

        try {
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: queryText,
                    voice: this.voiceEnabled
                })
            });

            const latency = Date.now() - startTime;
            if (this.dom.latencyDisplay) {
                this.dom.latencyDisplay.textContent = `${latency}ms`;
            }

            if (!response.ok) {
                throw new Error(`Server returned HTTP ${response.status}`);
            }

            const data = await response.json();
            const answer = data.answer || "Subsystem completed command with no textual output.";
            const decisions = data.decision || [];

            // Update Last Decision Box
            if (this.dom.lastDecisionText) {
                this.dom.lastDecisionText.innerHTML = decisions.map(d => `<div>• <strong>[${data.type.toUpperCase()}]</strong> ${d}</div>`).join('');
            }

            // Play notification sound
            if (window.omnisSFX) window.omnisSFX.playResponse();

            // Render AI response
            this.appendChatMessage("OMNIS", answer, decisions, false, data.target_url);

            // If a URL needs to be opened, launch it in browser window as well
            if (data.target_url) {
                try {
                    window.open(data.target_url, '_blank');
                } catch (e) {
                    console.log("Browser window.open blocked:", e);
                }
            }

            // If voice output enabled and backend didn't play audio directly, use client browser TTS fallback
            if (this.voiceEnabled && !data.audio_spoken) {
                this.speakBrowserTTS(answer);
            } else {
                this.updateSystemState('STANDBY');
            }

            // If an image generation query occurred, refresh gallery after a short delay
            if (data.type === 'image_generation') {
                setTimeout(() => this.fetchGallery(), 6000);
            }

        } catch (error) {
            console.error("Direct Query Error:", error);
            this.updateSystemState('STANDBY');
            this.appendChatMessage("OMNIS", `Neural Engine notice: Could not contact backend at /api/query (${error.message}). Please verify that 'python app.py' is running.`, ["SYSTEM_ERROR"]);
        }
    }

    speakBrowserTTS(text) {
        if (!('speechSynthesis' in window) || !this.voiceEnabled) {
            this.updateSystemState('STANDBY');
            return;
        }

        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = this.speechLang;
        utterance.rate = 1.05;
        utterance.pitch = 1.0;

        utterance.onstart = () => {
            this.updateSystemState('SPEAKING');
        };

        utterance.onend = () => {
            this.updateSystemState('STANDBY');
        };

        utterance.onerror = () => {
            this.updateSystemState('STANDBY');
        };

        window.speechSynthesis.speak(utterance);
    }

    // ================== CHAT RENDERING ==================

    appendChatMessage(sender, text, decisions = [], isUser = false, targetUrl = null) {
        if (!this.dom.chatStream) return;

        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        const card = document.createElement('div');
        card.className = `chat-message ${isUser ? 'user-message' : 'assistant-message'}`;

        const decisionTags = decisions.length ? `[DMM: ${decisions[0].split(' ')[0].toUpperCase()}]` : '[DIRECTIVE]';
        const linkBadge = targetUrl ? `<div><a href="${targetUrl}" target="_blank" rel="noopener noreferrer" class="hud-link-btn">🔗 Open ${targetUrl}</a></div>` : '';

        card.innerHTML = `
            <div class="msg-header">
                <span class="msg-sender"><span class="sender-badge">${sender}</span> ${isUser ? 'OPERATOR' : 'NEURAL CORE'}</span>
                <span class="msg-time">${timeStr}</span>
            </div>
            <div class="msg-body">
                ${this.formatMarkdown(text)}
                ${linkBadge}
            </div>
            <div class="msg-footer">
                <span class="dmm-tag">${decisionTags}</span>
                ${!isUser ? `<button class="speech-replay-btn" data-text="${encodeURIComponent(text)}">🔊 Listen</button>` : ''}
            </div>
        `;

        this.dom.chatStream.appendChild(card);
        this.dom.chatStream.scrollTop = this.dom.chatStream.scrollHeight;

        // Replay button listener
        const replayBtn = card.querySelector('.speech-replay-btn');
        if (replayBtn) {
            replayBtn.addEventListener('click', () => {
                const rawText = decodeURIComponent(replayBtn.getAttribute('data-text'));
                this.speakBrowserTTS(rawText);
            });
        }

        // Update total message count
        const total = this.dom.chatStream.querySelectorAll('.chat-message').length;
        if (this.dom.messageCount) {
            this.dom.messageCount.textContent = `${total} Directives Logged`;
        }
    }

    formatMarkdown(text) {
        if (!text) return "";
        let formatted = text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");

        // Code blocks
        formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        // Inline code
        formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
        // Bold
        formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        // Italic
        formatted = formatted.replace(/\*([^*]+)\*/g, '<em>$1</em>');
        // Linebreaks
        formatted = formatted.replace(/\n/g, '<br>');

        return formatted;
    }

    // ================== DATA FETCHERS ==================

    async fetchTelemetry() {
        try {
            const res = await fetch('/api/status');
            if (res.ok) {
                const data = await res.json();
                if (this.dom.cpuVal && data.telemetry) {
                    this.dom.cpuVal.textContent = `${Math.round(data.telemetry.cpu)}%`;
                    if (this.dom.cpuBar) this.dom.cpuBar.style.width = `${Math.min(data.telemetry.cpu, 100)}%`;
                }
                if (this.dom.memVal && data.telemetry) {
                    this.dom.memVal.textContent = `${Math.round(data.telemetry.memory)}%`;
                    if (this.dom.memBar) this.dom.memBar.style.width = `${Math.min(data.telemetry.memory, 100)}%`;
                }
                if (data.system_name) this.currentAssistantName = data.system_name;
                if (data.user_name) this.currentUserName = data.user_name;

                // Update settings checklist
                const kCohere = document.getElementById('keyCohere');
                const kGroq = document.getElementById('keyGroq');
                if (kCohere && data.modules) kCohere.textContent = data.modules.dmm_cohere;
                if (kGroq && data.modules) kGroq.textContent = data.modules.llm_groq;
            }
        } catch (e) {
            // Backend offline or unreachable
        }
    }

    async fetchChatLog() {
        try {
            const res = await fetch('/api/chatlog');
            if (res.ok) {
                const logs = await res.json();
                if (Array.isArray(logs) && logs.length > 0) {
                    logs.slice(-15).forEach(entry => {
                        if (entry.user) this.appendChatMessage(this.currentUserName, entry.user, ["USER_LOG"], true);
                        if (entry.assistant) this.appendChatMessage("OMNIS", entry.assistant, entry.decision || ["STORED_LOG"], false);
                    });
                }
            }
        } catch (e) {
            console.log("Chatlog fetch error:", e);
        }
    }

    async fetchGallery() {
        if (!this.dom.galleryGrid) return;
        try {
            const res = await fetch('/api/images');
            if (res.ok) {
                const images = await res.json();
                if (Array.isArray(images) && images.length > 0) {
                    this.dom.galleryGrid.innerHTML = '';
                    images.forEach(img => {
                        const card = document.createElement('div');
                        card.className = 'gallery-card';
                        card.innerHTML = `
                            <img src="${img.url}" alt="${img.filename}">
                            <div class="gallery-caption">${img.filename}</div>
                        `;
                        card.addEventListener('click', () => {
                            this.openLightbox(img.url, img.filename);
                        });
                        this.dom.galleryGrid.appendChild(card);
                    });
                }
            }
        } catch (e) {
            console.log("Gallery fetch error:", e);
        }
    }

    openLightbox(url, title) {
        if (!this.dom.imageLightboxModal) return;
        this.dom.lightboxImage.src = url;
        this.dom.lightboxCaption.textContent = title;
        this.dom.imageLightboxModal.classList.add('open');
        if (window.omnisSFX) window.omnisSFX.playTick();
    }

    saveSettings() {
        const aName = document.getElementById('configAssistantName');
        const uName = document.getElementById('configUserName');
        const sLang = document.getElementById('configSpeechLang');

        if (aName) this.currentAssistantName = aName.value.trim() || "OMNIS";
        if (uName) this.currentUserName = uName.value.trim() || "Sir";
        if (sLang) {
            this.speechLang = sLang.value;
            if (this.recognition) this.recognition.lang = this.speechLang;
        }

        if (window.omnisSFX) window.omnisSFX.playResponse();
    }

    exportChatHistory() {
        const messages = [];
        document.querySelectorAll('.chat-message').forEach(msg => {
            const sender = msg.querySelector('.msg-sender')?.textContent.trim() || 'Unknown';
            const body = msg.querySelector('.msg-body')?.textContent.trim() || '';
            const time = msg.querySelector('.msg-time')?.textContent.trim() || '';
            messages.push(`[${time}] ${sender}: ${body}`);
        });

        const blob = new Blob([messages.join('\n\n')], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `OMNIS_Chat_Export_${new Date().toISOString().slice(0, 10)}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    }
}

// Start application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.omnis = new OmnisApp();
});

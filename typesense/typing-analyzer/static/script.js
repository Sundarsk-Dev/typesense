/**
 * Typesense - Advanced Typing Pattern Analyzer
 * Tracks typing speed, pauses, corrections, and analyzes mood patterns
 */

class TypingAnalyzer {
    constructor() {
        this.state = {
            isActive: false,
            startTime: null,
            endTime: null,
            duration: 0,
            keystrokes: [],
            backspaces: 0,
            totalCharacters: 0,
            pauseThreshold: 500, // ms to consider as pause
            lastKeystrokeTime: null,
            totalPauseTime: 0,
            timer: null
        };
        
        this.elements = {
            typingBox: document.getElementById('typingBox'),
            timer: document.getElementById('timer'),
            result: document.getElementById('result'),
            charCount: document.getElementById('charCount'),
            characterCount: document.getElementById('characterCount'),
            liveStats: document.getElementById('liveStats'),
            liveWPM: document.getElementById('liveWPM'),
            liveBackspaces: document.getElementById('liveBackspaces'),
            resetBtn: document.getElementById('resetBtn'),
            durationBtns: document.querySelectorAll('.duration-btn')
        };
        
        this.init();
    }
    
    init() {
        // Attach event listeners
        this.elements.durationBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const duration = parseInt(btn.dataset.duration);
                this.startTest(duration);
            });
        });
        
        this.elements.typingBox.addEventListener('input', (e) => this.handleInput(e));
        this.elements.typingBox.addEventListener('keydown', (e) => this.handleKeydown(e));
        
        if (this.elements.resetBtn) {
            this.elements.resetBtn.addEventListener('click', () => this.reset());
        }
    }
    
    startTest(duration) {
        this.reset();
        this.state.duration = duration;
        this.state.isActive = true;
        this.state.startTime = Date.now();
        
        // UI updates
        this.elements.typingBox.disabled = false;
        this.elements.typingBox.placeholder = "Start typing...";
        this.elements.typingBox.focus();
        this.elements.typingBox.classList.add('typing-active');
        
        // Show live stats
        this.elements.characterCount.classList.remove('hidden');
        this.elements.liveStats.classList.remove('hidden');
        
        // Disable duration buttons during test
        this.elements.durationBtns.forEach(btn => btn.disabled = true);
        
        // Start countdown timer
        this.startTimer(duration);
    }
    
    startTimer(duration) {
        let remaining = duration;
        this.updateTimerDisplay(remaining);
        
        this.state.timer = setInterval(() => {
            remaining--;
            this.updateTimerDisplay(remaining);
            
            // Update live WPM
            if (this.state.totalCharacters > 0) {
                const elapsed = (Date.now() - this.state.startTime) / 1000;
                const wpm = this.calculateWPM(this.state.totalCharacters, elapsed);
                this.elements.liveWPM.textContent = Math.round(wpm);
            }
            
            if (remaining <= 0) {
                this.endTest();
            }
        }, 1000);
    }
    
    updateTimerDisplay(seconds) {
        if (seconds > 0) {
            this.elements.timer.textContent = `Time remaining: ${seconds}s`;
            this.elements.timer.className = seconds <= 3 ? 'text-2xl font-bold text-red-400' : 'text-2xl font-bold text-yellow-300';
        } else {
            this.elements.timer.textContent = "Time's up!";
        }
    }
    
    handleInput(event) {
        if (!this.state.isActive) return;
        
        const currentTime = Date.now();
        
        // Track pauses
        if (this.state.lastKeystrokeTime) {
            const timeSinceLastKey = currentTime - this.state.lastKeystrokeTime;
            if (timeSinceLastKey > this.state.pauseThreshold) {
                this.state.totalPauseTime += timeSinceLastKey;
            }
        }
        
        // Update character count
        this.state.totalCharacters = event.target.value.length;
        this.elements.charCount.textContent = this.state.totalCharacters;
        
        // Record keystroke timing
        this.state.keystrokes.push({
            timestamp: currentTime,
            charCount: this.state.totalCharacters
        });
        
        this.state.lastKeystrokeTime = currentTime;
    }
    
    handleKeydown(event) {
        if (!this.state.isActive) return;
        
        // Track backspaces
        if (event.key === 'Backspace' || event.key === 'Delete') {
            this.state.backspaces++;
            this.elements.liveBackspaces.textContent = this.state.backspaces;
        }
    }
    
    calculateWPM(characters, seconds) {
        // Average word length is 5 characters
        const words = characters / 5;
        const minutes = seconds / 60;
        return minutes > 0 ? words / minutes : 0;
    }
    
    calculateCPS(characters, seconds) {
        return seconds > 0 ? characters / seconds : 0;
    }
    
    async endTest() {
        this.state.isActive = false;
        this.state.endTime = Date.now();
        clearInterval(this.state.timer);
        
        // Disable typing box
        this.elements.typingBox.disabled = true;
        this.elements.typingBox.classList.remove('typing-active');
        
        // Calculate metrics
        const totalSeconds = (this.state.endTime - this.state.startTime) / 1000;
        const wpm = this.calculateWPM(this.state.totalCharacters, totalSeconds);
        const cps = this.calculateCPS(this.state.totalCharacters, totalSeconds);
        
        // Prepare data for analysis
        const analysisData = {
            wpm: wpm,
            cps: cps,
            pauses: this.state.totalPauseTime,
            backspaces: this.state.backspaces,
            duration: this.state.duration,
            totalCharacters: this.state.totalCharacters
        };
        
        // Send for analysis
        try {
            const response = await this.sendAnalysis(analysisData);
            this.displayResults(response);
        } catch (error) {
            console.error('Analysis failed:', error);
            this.displayError('Failed to analyze typing pattern. Please try again.');
        }
    }
    
    async sendAnalysis(data) {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    displayResults(data) {
        const resultElement = this.elements.result;
        resultElement.classList.remove('hidden');
        
        // Create detailed result message
        const resultHTML = `
            <div class="space-y-2">
                <p class="text-2xl font-bold text-green-400">${data.mood}</p>
                <div class="text-sm text-gray-400 mt-2">
                    <span class="mr-4">Score: ${data.score}</span>
                    <span class="mr-4">WPM: ${data.metrics.wpm}</span>
                    <span>Accuracy: ${data.metrics.accuracy}%</span>
                </div>
            </div>
        `;
        
        resultElement.innerHTML = resultHTML;
        
        // Show reset button
        this.elements.resetBtn.classList.remove('hidden');
        
        // Animate result appearance
        resultElement.style.opacity = '0';
        setTimeout(() => {
            resultElement.style.opacity = '1';
        }, 100);
    }
    
    displayError(message) {
        const resultElement = this.elements.result;
        resultElement.classList.remove('hidden');
        resultElement.innerHTML = `<p class="text-red-400">${message}</p>`;
        this.elements.resetBtn.classList.remove('hidden');
    }
    
    reset() {
        // Reset state
        this.state = {
            isActive: false,
            startTime: null,
            endTime: null,
            duration: 0,
            keystrokes: [],
            backspaces: 0,
            totalCharacters: 0,
            lastKeystrokeTime: null,
            totalPauseTime: 0,
            timer: null
        };
        
        // Reset UI
        this.elements.typingBox.value = '';
        this.elements.typingBox.disabled = true;
        this.elements.typingBox.placeholder = 'Choose a duration to begin...';
        this.elements.typingBox.classList.remove('typing-active');
        
        this.elements.timer.textContent = '';
        this.elements.result.classList.add('hidden');
        this.elements.resetBtn.classList.add('hidden');
        this.elements.characterCount.classList.add('hidden');
        this.elements.liveStats.classList.add('hidden');
        
        this.elements.charCount.textContent = '0';
        this.elements.liveWPM.textContent = '0';
        this.elements.liveBackspaces.textContent = '0';
        
        // Re-enable duration buttons
        this.elements.durationBtns.forEach(btn => btn.disabled = false);
        
        clearInterval(this.state.timer);
    }
}

// Initialize the analyzer when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.typingAnalyzer = new TypingAnalyzer();
    });
} else {
    window.typingAnalyzer = new TypingAnalyzer();
}

/**
 * Audio Recording Module
 * Handles microphone recording functionality
 */

class AudioRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.stream = null;
        this.isRecording = false;
        this.startTime = null;
        this.timerInterval = null;
    }

    /**
     * Check if browser supports recording
     */
    isSupported() {
        return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
    }

    /**
     * Start recording
     */
    async startRecording() {
        if (!this.isSupported()) {
            throw new Error('Audio recording not supported in this browser');
        }

        try {
            // Request microphone access
            this.stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 16000
                }
            });

            // Create media recorder
            const options = { mimeType: 'audio/webm' };

            // Fallback for Safari
            if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                options.mimeType = 'audio/mp4';
            }

            this.mediaRecorder = new MediaRecorder(this.stream, options);
            this.audioChunks = [];

            // Handle data available
            this.mediaRecorder.addEventListener('dataavailable', (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            });

            // Start recording
            this.mediaRecorder.start();
            this.isRecording = true;
            this.startTime = Date.now();

            console.log('Recording started');
        } catch (error) {
            console.error('Error starting recording:', error);
            throw new Error('Failed to access microphone. Please grant permission.');
        }
    }

    /**
     * Stop recording
     * @returns {Promise<Blob>} - Recorded audio blob
     */
    async stopRecording() {
        return new Promise((resolve, reject) => {
            if (!this.mediaRecorder || !this.isRecording) {
                reject(new Error('No active recording'));
                return;
            }

            this.mediaRecorder.addEventListener('stop', () => {
                const audioBlob = new Blob(this.audioChunks, {
                    type: this.mediaRecorder.mimeType
                });

                // Stop all tracks
                if (this.stream) {
                    this.stream.getTracks().forEach(track => track.stop());
                }

                this.isRecording = false;
                console.log('Recording stopped');

                resolve(audioBlob);
            });

            this.mediaRecorder.stop();
        });
    }

    /**
     * Get recording duration in seconds
     */
    getDuration() {
        if (!this.startTime) return 0;
        return Math.floor((Date.now() - this.startTime) / 1000);
    }

    /**
     * Format duration as MM:SS
     */
    getFormattedDuration() {
        const duration = this.getDuration();
        const minutes = Math.floor(duration / 60);
        const seconds = duration % 60;
        return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }

    /**
     * Cancel recording
     */
    cancelRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();

            if (this.stream) {
                this.stream.getTracks().forEach(track => track.stop());
            }

            this.isRecording = false;
            this.audioChunks = [];
        }
    }

    /**
     * Convert blob to File
     */
    blobToFile(blob, filename = 'recording.webm') {
        return new File([blob], filename, {
            type: blob.type,
            lastModified: Date.now()
        });
    }
}

// Export singleton instance
const recorder = new AudioRecorder();

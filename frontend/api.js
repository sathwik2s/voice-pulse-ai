/**
 * API Communication Module
 * Handles all backend communication
 */

// Use environment variable if provided, otherwise default to localhost
// For Vercel deployment, you can set this in your dashboard or a config file
const API_BASE_URL = window.VOICEPULSE_API_URL || 'http://localhost:5000';

class VoicePulseAPI {
    constructor(baseUrl = API_BASE_URL) {
        this.baseUrl = baseUrl;
    }

    /**
     * Check backend health
     */
    async healthCheck() {
        try {
            const response = await fetch(`${this.baseUrl}/health`);
            return await response.json();
        } catch (error) {
            console.error('Health check failed:', error);
            throw error;
        }
    }

    /**
     * Analyze audio file
     * @param {File} audioFile - Audio file to analyze
     * @param {Function} onProgress - Progress callback
     */
    async analyzeAudio(audioFile, onProgress = null) {
        try {
            const formData = new FormData();
            formData.append('audio', audioFile);

            const xhr = new XMLHttpRequest();

            return new Promise((resolve, reject) => {
                // Progress tracking
                if (onProgress) {
                    xhr.upload.addEventListener('progress', (e) => {
                        if (e.lengthComputable) {
                            const percentComplete = (e.loaded / e.total) * 100;
                            onProgress(percentComplete);
                        }
                    });
                }

                // Load handler
                xhr.addEventListener('load', () => {
                    if (xhr.status === 200) {
                        try {
                            const response = JSON.parse(xhr.responseText);
                            resolve(response);
                        } catch (error) {
                            reject(new Error('Invalid response format'));
                        }
                    } else {
                        try {
                            const error = JSON.parse(xhr.responseText);
                            reject(new Error(error.error || 'Analysis failed'));
                        } catch {
                            reject(new Error(`Server error: ${xhr.status}`));
                        }
                    }
                });

                // Error handler
                xhr.addEventListener('error', () => {
                    reject(new Error('Network error'));
                });

                // Timeout handler
                xhr.addEventListener('timeout', () => {
                    reject(new Error('Request timeout'));
                });

                // Send request
                xhr.open('POST', `${this.baseUrl}/analyze`);
                xhr.timeout = 300000; // 5 minutes
                xhr.send(formData);
            });
        } catch (error) {
            console.error('Analysis error:', error);
            throw error;
        }
    }

    /**
     * Get saved report
     * @param {string} analysisId - Analysis ID
     */
    async getReport(analysisId) {
        try {
            const response = await fetch(`${this.baseUrl}/report/${analysisId}`);
            
            if (!response.ok) {
                throw new Error('Report not found');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching report:', error);
            throw error;
        }
    }

    /**
     * Download report as JSON
     * @param {string} analysisId - Analysis ID
     */
    downloadReport(analysisId) {
        window.open(`${this.baseUrl}/download/${analysisId}`, '_blank');
    }

    /**
     * Quick analyze (single prediction)
     * @param {File} audioFile - Audio file
     */
    async quickAnalyze(audioFile) {
        try {
            const formData = new FormData();
            formData.append('audio', audioFile);

            const response = await fetch(`${this.baseUrl}/quick-analyze`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Quick analysis failed');
            }

            return await response.json();
        } catch (error) {
            console.error('Quick analysis error:', error);
            throw error;
        }
    }
}

// Export singleton instance
const api = new VoicePulseAPI();

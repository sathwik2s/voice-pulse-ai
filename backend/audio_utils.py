"""Audio Processing Utilities

Handles audio loading, conversion, and temporal segmentation.

Note: librosa depends on `audioread`, which may attempt to locate ffmpeg on import.
On Windows (especially in venv-only installs), ffmpeg may not be on PATH.
We proactively add the `imageio-ffmpeg` binary to PATH to avoid runtime warnings and
to ensure decoding/conversion works for compressed formats.
"""

import os
import subprocess
import logging
from shutil import which


def _ensure_ffmpeg_on_path() -> None:
    """Make an ffmpeg binary discoverable via PATH.

    If ffmpeg is already on PATH, do nothing.
    Otherwise, try `imageio-ffmpeg`'s bundled ffmpeg.
    """
    if which("ffmpeg"):
        return

    try:
        import imageio_ffmpeg

        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        if ffmpeg_exe and os.path.exists(ffmpeg_exe):
            ffmpeg_dir = os.path.dirname(ffmpeg_exe)
            os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
    except Exception:
        # If we can't find ffmpeg here, the converter will raise a helpful error later.
        return


_ensure_ffmpeg_on_path()

import librosa
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioProcessor:
    """Handles audio preprocessing and segmentation"""
    
    TARGET_SR = 16000  # Target sampling rate (16kHz)
    WINDOW_SIZE = 2.0  # Window size in seconds
    OVERLAP = 1.0      # Overlap in seconds
    
    def __init__(self):
        self.ffmpeg_exe = None
        self._configure_ffmpeg()

    def _configure_ffmpeg(self):
        """Ensure pydub can find an ffmpeg binary for mp3/m4a/ogg/webm conversion."""
        try:
            ffmpeg_on_path = which('ffmpeg')
            if ffmpeg_on_path:
                self.ffmpeg_exe = ffmpeg_on_path
                logger.info(f"Using ffmpeg from PATH: {self.ffmpeg_exe}")
                return

            try:
                import imageio_ffmpeg

                ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
                if ffmpeg_exe and os.path.exists(ffmpeg_exe):
                    self.ffmpeg_exe = ffmpeg_exe
                    logger.info(f"Using ffmpeg via imageio-ffmpeg: {ffmpeg_exe}")
            except Exception as e:
                logger.warning(f"FFmpeg not found and imageio-ffmpeg not available: {e}")
        except Exception as e:
            logger.warning(f"Failed to configure ffmpeg: {e}")
    
    def load_audio(self, file_path):
        """
        Load and preprocess audio file
        
        Args:
            file_path: path to audio file
            
        Returns:
            tuple: (audio_array, sampling_rate)
        """
        try:
            # Validate file_path
            if file_path is None:
                raise ValueError("File path is None")
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            logger.info(f"Loading audio file: {file_path}")
            
            # Get file extension
            ext = os.path.splitext(file_path)[1].lower()
            
            # Convert to WAV if needed (for mp3, m4a, ogg, webm)
            if ext in ['.mp3', '.m4a', '.ogg', '.webm']:
                converted_path = self._convert_to_wav(file_path)
                if converted_path and os.path.exists(converted_path):
                    file_path = converted_path
            
            # Load audio with librosa
            audio, sr = librosa.load(file_path, sr=self.TARGET_SR, mono=True)
            
            logger.info(f"Audio loaded: duration={len(audio)/sr:.2f}s, sr={sr}Hz")
            
            return audio, sr
            
        except Exception as e:
            logger.error(f"Error loading audio: {e}")
            raise
    
    def _convert_to_wav(self, file_path):
        """Convert audio file to WAV format"""
        try:
            if not file_path or not os.path.exists(file_path):
                logger.error(f"Invalid file path for conversion: {file_path}")
                return None
            
            logger.info(f"Converting {file_path} to WAV")

            if not self.ffmpeg_exe or not os.path.exists(self.ffmpeg_exe):
                raise RuntimeError(
                    "Audio conversion failed (missing ffmpeg). Install ffmpeg or install the Python package "
                    "'imageio-ffmpeg' so the backend can decode mp3/m4a/ogg/webm."
                )

            wav_path = file_path.rsplit('.', 1)[0] + '_converted.wav'

            # Convert to mono PCM WAV @ TARGET_SR
            cmd = [
                self.ffmpeg_exe,
                '-y',
                '-i', file_path,
                '-ac', '1',
                '-ar', str(self.TARGET_SR),
                '-f', 'wav',
                wav_path
            ]

            completed = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )

            if completed.returncode != 0 or not os.path.exists(wav_path):
                stderr = (completed.stderr or '').strip()
                logger.error(f"ffmpeg conversion failed (code {completed.returncode}): {stderr}")
                raise RuntimeError(
                    "Audio conversion failed while decoding the uploaded audio. "
                    "Ensure the file is a valid audio recording."
                )

            logger.info(f"Conversion successful: {wav_path}")
            return wav_path
            
        except Exception as e:
            logger.error(f"Error converting audio: {e}")
            raise
    
    def segment_audio(self, audio, sr):
        """
        Segment audio into overlapping windows
        
        Args:
            audio: numpy array of audio samples
            sr: sampling rate
            
        Returns:
            list of tuples: [(segment_array, start_time, end_time), ...]
        """
        segments = []
        
        window_samples = int(self.WINDOW_SIZE * sr)
        hop_samples = int((self.WINDOW_SIZE - self.OVERLAP) * sr)
        
        total_duration = len(audio) / sr
        
        start_sample = 0
        while start_sample < len(audio):
            end_sample = min(start_sample + window_samples, len(audio))
            
            # Extract segment
            segment = audio[start_sample:end_sample]
            
            # Pad if necessary (last segment might be shorter)
            if len(segment) < window_samples:
                segment = np.pad(segment, (0, window_samples - len(segment)), mode='constant')
            
            # Calculate timestamps
            start_time = start_sample / sr
            end_time = end_sample / sr
            
            segments.append({
                'audio': segment,
                'start_time': start_time,
                'end_time': end_time,
                'start_formatted': self._format_time(start_time),
                'end_formatted': self._format_time(end_time)
            })
            
            start_sample += hop_samples
            
            # Break if we've reached the end
            if end_sample >= len(audio):
                break
        
        logger.info(f"Created {len(segments)} segments from {total_duration:.2f}s audio")
        
        return segments
    
    def _format_time(self, seconds):
        """Format seconds as MM:SS"""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"
    
    def get_audio_duration(self, file_path):
        """Get duration of audio file in seconds"""
        try:
            audio, sr = self.load_audio(file_path)
            return len(audio) / sr
        except Exception as e:
            logger.error(f"Error getting audio duration: {e}")
            return 0
    
    def validate_audio(self, file_path, max_duration=600):
        """
        Validate audio file
        
        Args:
            file_path: path to audio file
            max_duration: maximum allowed duration in seconds
            
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Check file exists
            if not os.path.exists(file_path):
                return False, "File does not exist"
            
            # Check file size (max 50MB)
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            if file_size > 50:
                return False, f"File too large: {file_size:.2f}MB (max 50MB)"
            
            # Check duration
            duration = self.get_audio_duration(file_path)
            if duration > max_duration:
                return False, f"Audio too long: {duration:.2f}s (max {max_duration}s)"
            
            if duration < 0.5:
                return False, "Audio too short (minimum 0.5s)"
            
            return True, "Valid"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"

"""
Emotion Recognition Model Handler
Loads and manages the Wav2Vec2 emotion recognition model
"""

import os
from typing import Any, Optional, cast
import torch
import torchaudio
from transformers import AutoFeatureExtractor, Wav2Vec2ForSequenceClassification, Wav2Vec2Processor
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmotionModel:
    """Handles emotion recognition using pre-trained Wav2Vec2 model"""
    
    # Emotion label mapping
    EMOTION_LABELS = {
        0: "neutral",
        1: "happy",
        2: "sad",
        3: "angry",
        4: "fear",
        5: "disgust",
        6: "surprise"
    }
    
    def __init__(self, model_name="superb/wav2vec2-base-superb-er"):
        """
        Initialize the emotion recognition model
        
        Args:
            model_name: HuggingFace model identifier
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")

        self.cache_dir = os.path.join(os.path.dirname(__file__), "hf_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.feature_extractor: Optional[Any] = None
        self.processor: Optional[Any] = None
        self.model: Any = None
        
        try:
            logger.info(f"Loading model: {model_name}")

            # Many audio classification repos don't ship tokenizer files.
            # Use a feature extractor (audio-only) instead of Wav2Vec2Processor (feature_extractor + tokenizer).
            self.feature_extractor = AutoFeatureExtractor.from_pretrained(
                model_name,
                cache_dir=self.cache_dir
            )

            self.model = cast(Any, Wav2Vec2ForSequenceClassification.from_pretrained(
                model_name,
                cache_dir=self.cache_dir,
                use_safetensors=False
            ))
            self.model = self.model.to(self.device)
            self.model.eval()
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.exception(f"Error loading model: {e}")
            # Fallback: try the older processor path (in case the repo does have tokenizer files)
            try:
                logger.info("Retrying with Wav2Vec2Processor fallback...")
                self.processor = Wav2Vec2Processor.from_pretrained(
                    model_name,
                    cache_dir=self.cache_dir
                )
                self.model = cast(Any, Wav2Vec2ForSequenceClassification.from_pretrained(
                    model_name,
                    cache_dir=self.cache_dir,
                    use_safetensors=False
                ))
                self.model = self.model.to(self.device)
                self.model.eval()
                logger.info("Model loaded successfully using processor fallback")
                return
            except Exception as e2:
                logger.exception(f"Processor fallback also failed: {e2}")
            raise
    
    def predict_emotion(self, audio_array, sampling_rate=16000):
        """
        Predict emotion from audio segment
        
        Args:
            audio_array: numpy array of audio samples
            sampling_rate: audio sampling rate (default 16kHz)
            
        Returns:
            dict: {
                'emotion': str,
                'confidence': float,
                'all_scores': dict
            }
        """
        try:
            # Ensure audio is the right shape
            if len(audio_array.shape) > 1:
                audio_array = audio_array.mean(axis=1)  # Convert to mono
            
            # Process audio
            feature_extractor = self.feature_extractor
            processor = self.processor

            if feature_extractor is not None:
                inputs = feature_extractor(
                    audio_array,
                    sampling_rate=sampling_rate,
                    return_tensors="pt",
                    padding=True
                )
            else:
                if processor is None:
                    raise RuntimeError("Model processor is not initialized")

                inputs = processor(
                    audio_array,
                    sampling_rate=sampling_rate,
                    return_tensors="pt",
                    padding=True
                )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get predictions
            with torch.no_grad():
                logits = self.model(**inputs).logits
                probabilities = torch.nn.functional.softmax(logits, dim=-1)
            
            # Get top prediction
            predicted_id = int(torch.argmax(probabilities, dim=-1).item())
            confidence = probabilities[0][predicted_id].item()
            
            # Get all emotion scores
            all_scores = {}
            for idx, prob in enumerate(probabilities[0].cpu().numpy()):
                emotion_name = self.EMOTION_LABELS.get(idx, f"unknown_{idx}")
                all_scores[emotion_name] = float(prob)
            
            emotion = self.EMOTION_LABELS.get(predicted_id, "unknown")
            
            return {
                'emotion': emotion,
                'confidence': float(confidence),
                'all_scores': all_scores
            }
            
        except Exception as e:
            logger.exception(f"Error in emotion prediction: {e}")
            raise
    
    def batch_predict(self, audio_segments, sampling_rate=16000):
        """
        Predict emotions for multiple audio segments
        
        Args:
            audio_segments: list of numpy arrays
            sampling_rate: audio sampling rate
            
        Returns:
            list of prediction dictionaries
        """
        predictions = []
        for segment in audio_segments:
            pred = self.predict_emotion(segment, sampling_rate)
            predictions.append(pred)
        return predictions


# Global model instance (singleton pattern for efficiency)
_model_instance = None

def get_model():
    """Get or create the global model instance"""
    global _model_instance
    if _model_instance is None:
        _model_instance = EmotionModel()
    return _model_instance

"""
Main Emotion Analysis Pipeline
Orchestrates the complete emotion intelligence workflow
"""

import logging
import numpy as np
from audio_utils import AudioProcessor
from emotion_model import get_model
from transition_logic import TransitionDetector
from sentiment_map import SentimentMapper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmotionPipeline:
    """Main pipeline for speech emotion intelligence"""
    
    def __init__(self):
        self.audio_processor = AudioProcessor()
        self.transition_detector = TransitionDetector()
        self.sentiment_mapper = SentimentMapper()
        self.model = None  # Lazy loading
    
    def _ensure_model_loaded(self):
        """Ensure the emotion model is loaded"""
        if self.model is None:
            logger.info("Loading emotion model...")
            self.model = get_model()
    
    def analyze_audio(self, file_path):
        """
        Complete emotion analysis pipeline
        
        Args:
            file_path: path to audio file
            
        Returns:
            dict: complete analysis results
        """
        try:
            logger.info(f"Starting emotion analysis for: {file_path}")
            
            # Ensure model is loaded
            self._ensure_model_loaded()
            
            # Step 1: Load and validate audio
            logger.info("Step 1: Loading audio...")
            audio, sr = self.audio_processor.load_audio(file_path)
            duration = len(audio) / sr
            
            # Step 2: Segment audio
            logger.info("Step 2: Segmenting audio...")
            segments = self.audio_processor.segment_audio(audio, sr)
            
            # Step 3: Predict emotions for each segment
            logger.info(f"Step 3: Analyzing {len(segments)} segments...")
            timeline = []
            
            for i, segment_data in enumerate(segments):
                prediction = self.model.predict_emotion(
                    segment_data['audio'],
                    sampling_rate=sr
                )
                
                timeline_entry = {
                    'segment_id': i,
                    'start_time': segment_data['start_time'],
                    'end_time': segment_data['end_time'],
                    'start_formatted': segment_data['start_formatted'],
                    'end_formatted': segment_data['end_formatted'],
                    'emotion': prediction['emotion'],
                    'confidence': round(prediction['confidence'], 3),
                    'all_scores': prediction['all_scores']
                }
                
                timeline.append(timeline_entry)
            
            # Step 4: Detect transitions
            logger.info("Step 4: Detecting emotion transitions...")
            transitions = self.transition_detector.detect_transitions(timeline)
            
            # Step 5: Calculate distribution
            logger.info("Step 5: Calculating emotion distribution...")
            distribution = self.transition_detector.calculate_emotion_distribution(timeline)
            
            # Step 6: Add sentiment layer
            logger.info("Step 6: Adding sentiment analysis...")
            timeline_with_sentiment = self.sentiment_mapper.add_sentiment_to_timeline(timeline)
            overall_sentiment = self.sentiment_mapper.calculate_overall_sentiment(distribution)
            
            # Step 7: Generate confidence curve
            confidence_curve = [
                {
                    'time': entry['start_formatted'],
                    'time_seconds': entry['start_time'],
                    'confidence': entry['confidence'],
                    'emotion': entry['emotion']
                }
                for entry in timeline
            ]
            
            # Step 8: Generate heatmap data
            heatmap_data = self._generate_heatmap_data(timeline_with_sentiment)
            
            # Step 9: Emotional journey analysis
            journey_analysis = self.transition_detector.analyze_emotional_journey(timeline)
            
            # Compile results
            results = {
                'success': True,
                'metadata': {
                    'duration': round(duration, 2),
                    'total_segments': len(segments),
                    'sampling_rate': sr
                },
                'timeline': timeline_with_sentiment,
                'transitions': transitions,
                'distribution': distribution,
                'confidence_curve': confidence_curve,
                'heatmap_data': heatmap_data,
                'sentiment_analysis': overall_sentiment,
                'journey_analysis': journey_analysis
            }
            
            logger.info("Analysis complete!")
            return results
            
        except Exception as e:
            logger.error(f"Error in emotion pipeline: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_heatmap_data(self, timeline):
        """
        Generate heatmap data for emotion intensity visualization
        
        Args:
            timeline: list of emotion predictions
            
        Returns:
            list: heatmap data points
        """
        emotions = ['happy', 'sad', 'angry', 'neutral', 'fear', 'disgust', 'surprise']
        heatmap = []
        
        for entry in timeline:
            time_point = {
                'time': entry['start_formatted'],
                'time_seconds': entry['start_time']
            }
            
            # Add intensity for each emotion
            for emotion in emotions:
                score = entry['all_scores'].get(emotion, 0)
                time_point[emotion] = round(score, 3)
            
            heatmap.append(time_point)
        
        return heatmap
    
    def quick_analyze(self, file_path):
        """
        Quick analysis with just primary emotion and confidence
        
        Args:
            file_path: path to audio file
            
        Returns:
            dict: simplified results
        """
        try:
            self._ensure_model_loaded()
            
            # Load audio
            audio, sr = self.audio_processor.load_audio(file_path)
            
            # Get single prediction for entire audio
            prediction = self.model.predict_emotion(audio, sr)
            
            return {
                'success': True,
                'emotion': prediction['emotion'],
                'confidence': prediction['confidence']
            }
            
        except Exception as e:
            logger.error(f"Error in quick analysis: {e}")
            return {
                'success': False,
                'error': str(e)
            }

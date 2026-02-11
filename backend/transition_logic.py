"""
Emotion Transition Detection Logic
Detects and analyzes emotion changes over time
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TransitionDetector:
    """Detects emotion transitions and shift events"""
    
    def __init__(self, confidence_threshold=0.1):
        """
        Initialize transition detector
        
        Args:
            confidence_threshold: minimum confidence drop to consider significant
        """
        self.confidence_threshold = confidence_threshold
    
    def detect_transitions(self, timeline):
        """
        Detect emotion transition events
        
        Args:
            timeline: list of emotion predictions with timestamps
            
        Returns:
            list of transition events
        """
        transitions = []
        
        if len(timeline) < 2:
            return transitions
        
        for i in range(1, len(timeline)):
            prev = timeline[i - 1]
            curr = timeline[i]
            
            # Check if emotion changed
            if prev['emotion'] != curr['emotion']:
                confidence_drop = abs(prev['confidence'] - curr['confidence'])
                
                transition = {
                    'time': curr['start_formatted'],
                    'time_seconds': curr['start_time'],
                    'from_emotion': prev['emotion'],
                    'to_emotion': curr['emotion'],
                    'from_confidence': round(prev['confidence'], 3),
                    'to_confidence': round(curr['confidence'], 3),
                    'confidence_change': round(curr['confidence'] - prev['confidence'], 3),
                    'is_significant': confidence_drop > self.confidence_threshold
                }
                
                transitions.append(transition)
        
        logger.info(f"Detected {len(transitions)} emotion transitions")
        
        return transitions
    
    def get_dominant_emotions(self, timeline, top_n=3):
        """
        Get the most dominant emotions by duration
        
        Args:
            timeline: list of emotion predictions
            top_n: number of top emotions to return
            
        Returns:
            list of tuples: [(emotion, percentage), ...]
        """
        emotion_counts = {}
        
        for entry in timeline:
            emotion = entry['emotion']
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        total = len(timeline)
        emotion_percentages = [
            (emotion, (count / total) * 100)
            for emotion, count in emotion_counts.items()
        ]
        
        # Sort by percentage
        emotion_percentages.sort(key=lambda x: x[1], reverse=True)
        
        return emotion_percentages[:top_n]
    
    def calculate_emotion_distribution(self, timeline):
        """
        Calculate percentage distribution of emotions
        
        Args:
            timeline: list of emotion predictions
            
        Returns:
            dict: {emotion: percentage}
        """
        emotion_counts = {}
        
        for entry in timeline:
            emotion = entry['emotion']
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        total = len(timeline)
        distribution = {
            emotion: round((count / total) * 100, 2)
            for emotion, count in emotion_counts.items()
        }
        
        return distribution
    
    def get_emotion_stability_score(self, timeline):
        """
        Calculate how stable emotions are (fewer transitions = more stable)
        
        Args:
            timeline: list of emotion predictions
            
        Returns:
            float: stability score (0-1, higher = more stable)
        """
        if len(timeline) < 2:
            return 1.0
        
        transitions = self.detect_transitions(timeline)
        
        # Calculate stability (inverse of transition rate)
        transition_rate = len(transitions) / len(timeline)
        stability = max(0, 1 - transition_rate)
        
        return round(stability, 3)
    
    def analyze_emotional_journey(self, timeline):
        """
        Provide a high-level analysis of the emotional journey
        
        Args:
            timeline: list of emotion predictions
            
        Returns:
            dict: analysis summary
        """
        if not timeline:
            return {}
        
        transitions = self.detect_transitions(timeline)
        distribution = self.calculate_emotion_distribution(timeline)
        dominant = self.get_dominant_emotions(timeline, top_n=3)
        stability = self.get_emotion_stability_score(timeline)
        
        # Determine overall emotional tone
        if dominant:
            primary_emotion = dominant[0][0]
        else:
            primary_emotion = "neutral"
        
        return {
            'primary_emotion': primary_emotion,
            'total_transitions': len(transitions),
            'stability_score': stability,
            'dominant_emotions': [
                {'emotion': e, 'percentage': round(p, 2)}
                for e, p in dominant
            ],
            'emotional_variability': 'high' if len(transitions) > len(timeline) * 0.3 else 'low'
        }

"""
Sentiment Mapping Module
Maps emotions to sentiment polarity scores
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentimentMapper:
    """Maps emotions to sentiment categories and scores"""
    
    # Emotion to sentiment mapping
    EMOTION_TO_SENTIMENT = {
        'happy': 'positive',
        'surprise': 'positive',
        'neutral': 'neutral',
        'sad': 'negative',
        'angry': 'negative',
        'fear': 'negative',
        'disgust': 'negative'
    }
    
    # Sentiment polarity scores (-1 to +1)
    SENTIMENT_SCORES = {
        'happy': 0.8,
        'surprise': 0.6,
        'neutral': 0.0,
        'sad': -0.6,
        'angry': -0.8,
        'fear': -0.7,
        'disgust': -0.75
    }
    
    def __init__(self):
        pass
    
    def get_sentiment(self, emotion):
        """
        Get sentiment category for an emotion
        
        Args:
            emotion: emotion label (str)
            
        Returns:
            str: 'positive', 'neutral', or 'negative'
        """
        return self.EMOTION_TO_SENTIMENT.get(emotion.lower(), 'neutral')
    
    def get_sentiment_score(self, emotion):
        """
        Get numerical sentiment score for an emotion
        
        Args:
            emotion: emotion label (str)
            
        Returns:
            float: sentiment score between -1 and +1
        """
        return self.SENTIMENT_SCORES.get(emotion.lower(), 0.0)
    
    def calculate_overall_sentiment(self, emotion_distribution):
        """
        Calculate overall sentiment from emotion distribution
        
        Args:
            emotion_distribution: dict of {emotion: percentage}
            
        Returns:
            dict: {
                'score': float,
                'category': str,
                'breakdown': dict
            }
        """
        total_score = 0.0
        breakdown = {
            'positive': 0.0,
            'neutral': 0.0,
            'negative': 0.0
        }
        
        for emotion, percentage in emotion_distribution.items():
            score = self.get_sentiment_score(emotion)
            sentiment = self.get_sentiment(emotion)
            
            total_score += score * (percentage / 100)
            breakdown[sentiment] += percentage
        
        # Determine overall category
        if total_score > 0.2:
            category = 'positive'
        elif total_score < -0.2:
            category = 'negative'
        else:
            category = 'neutral'
        
        return {
            'score': round(total_score, 3),
            'category': category,
            'breakdown': breakdown
        }
    
    def add_sentiment_to_timeline(self, timeline):
        """
        Add sentiment information to timeline data
        
        Args:
            timeline: list of emotion predictions with timestamps
            
        Returns:
            list: timeline with sentiment added
        """
        enriched_timeline = []
        
        for entry in timeline:
            enriched_entry = entry.copy()
            emotion = entry.get('emotion', 'neutral')
            
            enriched_entry['sentiment'] = self.get_sentiment(emotion)
            enriched_entry['sentiment_score'] = self.get_sentiment_score(emotion)
            
            enriched_timeline.append(enriched_entry)
        
        return enriched_timeline

"""
Emotion Adapter - Adapts LLM responses based on child's emotional state
"""

from typing import Dict, Any, Optional
from enum import Enum


class EmotionalState(Enum):
    """Child's emotional states"""
    CALM = "calm"
    ENGAGED = "engaged"
    FRUSTRATED = "frustrated"
    ANXIOUS = "anxious"
    TIRED = "tired"
    HAPPY = "happy"


class EmotionAdapter:
    """Adapts feedback and activities based on emotional state"""
    
    # Emotional thresholds for detection
    EMOTIONAL_THRESHOLDS = {
        "anxiety": {
            "mean_f0": 350,
            "jitter": 0.03,
            "shimmer": 0.05,
            "hnr": 8
        },
        "frustration": {
            "mean_f0": 320,
            "jitter": 0.025,
            "shimmer": 0.045,
            "energy_dev": 0.3
        },
        "happiness": {
            "mean_f0": 280,
            "energy_dev": 0.15,
            "hnr": 15
        }
    }
    
    # Response styles for each emotional state
    RESPONSE_STYLES = {
        EmotionalState.ANXIOUS: {
            "tone": "soothing",
            "pace": "slow",
            "positivity_boost": 1.5,
            "encouragement_frequency": "high",
            "keywords": ["هادئ", "بهدوء", "تنفس", "ممتاز", "معاك"],
            "avoid": ["صعب", "غلط", "شد", "قوي"]
        },
        EmotionalState.FRUSTRATED: {
            "tone": "supportive",
            "pace": "normal",
            "positivity_boost": 1.3,
            "encouragement_frequency": "very_high",
            "keywords": ["معاك", "قادر", "بطل", "تحسن", "زي ما تحب"],
            "avoid": ["لسه", "لسا", "ضعيف"]
        },
        EmotionalState.CALM: {
            "tone": "neutral",
            "pace": "normal",
            "positivity_boost": 1.0,
            "encouragement_frequency": "normal",
            "keywords": ["ممتاز", "أحسنت", "تمام"],
            "avoid": []
        },
        EmotionalState.ENGAGED: {
            "tone": "energetic",
            "pace": "slightly_fast",
            "positivity_boost": 1.2,
            "encouragement_frequency": "normal",
            "keywords": ["رائع", "جميل", "تكملة", "زيادة"],
            "avoid": ["بس", "فقط"]
        },
        EmotionalState.HAPPY: {
            "tone": "celebratory",
            "pace": "fast",
            "positivity_boost": 1.5,
            "encouragement_frequency": "high",
            "keywords": ["ماشاء الله", "يا سلام", "أحلى", "جميل جداً"],
            "avoid": []
        },
        EmotionalState.TIRED: {
            "tone": "gentle",
            "pace": "very_slow",
            "positivity_boost": 1.2,
            "encouragement_frequency": "medium",
            "keywords": ["خلينا", "آخر", "قليل", "بعدين"],
            "avoid": ["زيادة", "كمان", "أسرع"]
        }
    }
    
    def detect_emotional_state(
        self,
        acoustic_features: Dict[str, float],
        performance: Optional[Dict[str, Any]] = None
    ) -> EmotionalState:
        """Detect child's emotional state from acoustic features"""
        
        if self._check_anxiety(acoustic_features):
            return EmotionalState.ANXIOUS
        
        if self._check_frustration(acoustic_features, performance):
            return EmotionalState.FRUSTRATED
        
        if self._check_happiness(acoustic_features):
            return EmotionalState.HAPPY
        
        if performance and performance.get("accuracy", 0) > 70:
            if performance.get("repetition_count", 0) < 2:
                return EmotionalState.ENGAGED
        
        if self._check_tiredness(acoustic_features, performance):
            return EmotionalState.TIRED
        
        return EmotionalState.CALM
    
    def _check_anxiety(self, features: Dict[str, float]) -> bool:
        """Check for anxiety signs in voice"""
        thresholds = self.EMOTIONAL_THRESHOLDS["anxiety"]
        
        if features.get("mean_f0", 0) > thresholds["mean_f0"]:
            return True
        if features.get("jitter", 0) > thresholds["jitter"]:
            return True
        if features.get("shimmer", 0) > thresholds["shimmer"]:
            return True
        if features.get("hnr", 10) < thresholds["hnr"]:
            return True
        
        return False
    
    def _check_frustration(self, features: Dict[str, float], performance: Optional[Dict]) -> bool:
        """Check for frustration signs"""
        thresholds = self.EMOTIONAL_THRESHOLDS["frustration"]
        
        # Acoustic indicators
        if (features.get("mean_f0", 0) > thresholds["mean_f0"] and
            features.get("energy_dev", 0) > thresholds["energy_dev"]):
            return True
        
        # Performance indicators
        if performance:
            if performance.get("repetition_count", 0) > 3:
                return True
            if performance.get("accuracy", 100) < 40:
                return True
            if performance.get("error_count", 0) > 5:
                return True
        
        return False
    
    def _check_happiness(self, features: Dict[str, float]) -> bool:
        """Check for happiness signs"""
        thresholds = self.EMOTIONAL_THRESHOLDS["happiness"]
        
        if (features.get("hnr", 0) > thresholds["hnr"] and
            features.get("energy_dev", 1) < thresholds["energy_dev"]):
            return True
        
        return False
    
    def _check_tiredness(self, features: Dict[str, float], performance: Optional[Dict]) -> bool:
        """Check for tiredness signs"""
        if performance:
            if performance.get("session_duration", 0) > 300:  # 5+ minutes
                return True
            if performance.get("consecutive_errors", 0) > 3:
                return True
        
        # Very low fundamental frequency (fatigued voice)
        if features.get("mean_f0", 250) < 200:
            return True
        
        return False
    
    def adapt_response(self, original_response: str, emotional_state: EmotionalState) -> str:
        """Adapt response based on emotional state"""
        
        if emotional_state == EmotionalState.CALM:
            return original_response
        
        style = self.RESPONSE_STYLES.get(emotional_state, self.RESPONSE_STYLES[EmotionalState.CALM])
        
        # Shorten for anxious/frustrated children
        if emotional_state in [EmotionalState.ANXIOUS, EmotionalState.FRUSTRATED]:
            sentences = original_response.split("。")
            if len(sentences) > 1:
                original_response = sentences[0]
            
            comfort = " معاك، أنا هنا لمساعدتك 🤗"
            original_response += comfort
        
        # Add energy for happy/engaged
        elif emotional_state in [EmotionalState.HAPPY, EmotionalState.ENGAGED]:
            if "🎉" not in original_response and "🌟" not in original_response:
                original_response += " 🎉🎉"
        
        # Add rest reminder for tired
        elif emotional_state == EmotionalState.TIRED:
            if "استراحة" not in original_response:
                original_response += " \nخلينا ناخد استراحة قصيرة ونكمل بعدين 🛋️"
        
        # Remove negative words for anxious/frustrated
        if emotional_state in [EmotionalState.ANXIOUS, EmotionalState.FRUSTRATED]:
            for avoid_word in style.get("avoid", []):
                original_response = original_response.replace(avoid_word, "👍")
        
        return original_response
    
    def get_activity_adjustment(self, emotional_state: EmotionalState) -> Dict[str, Any]:
        """Get activity difficulty adjustment based on emotional state"""
        adjustments = {
            EmotionalState.ANXIOUS: {
                "difficulty": "easier",
                "pace": "slower",
                "use_games": True,
                "duration_reduction": 0.5,
                "pause_frequency": "high"
            },
            EmotionalState.FRUSTRATED: {
                "difficulty": "easier",
                "pace": "normal",
                "use_games": True,
                "duration_reduction": 0.3,
                "pause_frequency": "high"
            },
            EmotionalState.ENGAGED: {
                "difficulty": "maintain",
                "pace": "normal",
                "use_games": False,
                "duration_reduction": 0,
                "pause_frequency": "normal"
            },
            EmotionalState.HAPPY: {
                "difficulty": "slightly_harder",
                "pace": "normal",
                "use_games": False,
                "duration_reduction": 0,
                "pause_frequency": "normal"
            },
            EmotionalState.TIRED: {
                "difficulty": "much_easier",
                "pace": "slower",
                "use_games": True,
                "duration_reduction": 0.7,
                "pause_frequency": "very_high"
            },
            EmotionalState.CALM: {
                "difficulty": "maintain",
                "pace": "normal",
                "use_games": False,
                "duration_reduction": 0,
                "pause_frequency": "normal"
            }
        }
        
        return adjustments.get(emotional_state, adjustments[EmotionalState.CALM])
    
    def should_intervene_therapeutically(self, emotional_state: EmotionalState, arousal_duration: int) -> bool:
        """Determine if therapeutic intervention is needed"""
        if emotional_state == EmotionalState.ANXIOUS and arousal_duration > 5:
            return True
        if emotional_state == EmotionalState.FRUSTRATED and arousal_duration > 30:
            return True
        if emotional_state == EmotionalState.TIRED and arousal_duration > 60:
            return True
        return False


# Singleton instance
emotion_adapter = EmotionAdapter()
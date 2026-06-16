"""
Feedback Generator - Main feedback generation module
"""

from typing import Dict, Any, Optional

from app.llm.llm_engine import llm_engine
from app.llm.prompt_manager import prompt_manager
from app.llm.emotion_adapter import emotion_adapter, EmotionalState


class FeedbackGenerator:
    """Generates therapeutic feedback using Gemini"""

    def __init__(self):
        """Initialize feedback generator"""

        self.last_emotional_state = EmotionalState.CALM
        self.state_duration = 0

    def generate_complete_feedback(
        self,
        analysis_result: Dict[str, Any],
        acoustic_features: Dict[str, float],
        problem_type: str,
        accuracy: float,
        session_count: int,
        performance_history: Optional[Dict] = None,
        child_name: str = None
    ) -> Dict[str, Any]:
        """
        Generate complete feedback dynamically using Gemini
        """

        # Detect emotional state
        emotional_state = emotion_adapter.detect_emotional_state(
            acoustic_features,
            performance_history
        )

        # Emotional state mapping
        state_mapping = {
            EmotionalState.HAPPY: "very_happy",
            EmotionalState.ENGAGED: "happy",
            EmotionalState.CALM: "neutral",
            EmotionalState.TIRED: "tired",
            EmotionalState.FRUSTRATED: "frustrated",
            EmotionalState.ANXIOUS: "anxious"
        }

        emotional_state_str = state_mapping.get(
            emotional_state,
            "neutral"
        )

        # Track emotional duration
        if emotional_state == self.last_emotional_state:
            self.state_duration += 1

        else:
            self.last_emotional_state = emotional_state
            self.state_duration = 0

        # Check intervention
        needs_intervention = (
            emotion_adapter.should_intervene_therapeutically(
                emotional_state,
                self.state_duration
            )
        )

        # ALWAYS USE GEMINI
        feedback = llm_engine.generate_feedback(
            analysis_result=analysis_result,
            accuracy=accuracy,
            exercise_correct=analysis_result.get(
                "exercise_correct",
                False
            ),
            emotional_state=emotional_state_str
        )

        # Keep raw Gemini response
        adapted_feedback = feedback

        # Add child name if needed
        if child_name:

            if child_name not in adapted_feedback:

                if emotional_state in [
                    EmotionalState.ANXIOUS,
                    EmotionalState.FRUSTRATED
                ]:

                    adapted_feedback = (
                        f"{child_name}، {adapted_feedback}"
                    )

        # Activity adjustments
        adjustments = emotion_adapter.get_activity_adjustment(
            emotional_state
        )

        return {
            "feedback": adapted_feedback,
            "emotional_state": emotional_state_str,
            "needs_intervention": needs_intervention,
            "activity_adjustments": adjustments
        }

    def generate_activity_instruction(
        self,
        problem_type: str,
        activity_name: str,
        variables: Dict[str, Any],
        emotional_state: str = "neutral"
    ) -> str:
        """Generate therapy instruction"""

        return llm_engine.generate_therapy_prompt(
            problem_type=problem_type,
            activity_name=activity_name,
            variables=variables,
            emotional_state=emotional_state
        )

    def reset(self):
        """Reset generator state"""

        self.last_emotional_state = EmotionalState.CALM
        self.state_duration = 0

        prompt_manager.reset_context()


# Singleton instance
feedback_generator = FeedbackGenerator()
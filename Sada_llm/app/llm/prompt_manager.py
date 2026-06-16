"""
Prompt Manager - Manages and renders prompts from JSON configuration
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path


class PromptManager:
    """Manages all prompts for SADA AI with Egyptian Arabic dialect support"""

    def __init__(self, prompt_file_path: Optional[str] = None):
        """Initialize prompt manager"""

        if prompt_file_path is None:
            prompt_file_path = (
                Path(__file__).parent.parent / "config" / "prompt.json"
            )

        self.prompts = self._load_prompts(prompt_file_path)
        self.emotional_state = "neutral"
        self.child_context = {}

    def _load_prompts(self, file_path) -> Dict:
        """Load prompts from JSON file"""

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)

        except FileNotFoundError:
            print(f"Prompt file not found: {file_path}")
            return self._get_default_prompts()

        except json.JSONDecodeError as e:
            print(f"Invalid JSON in prompt file: {e}")
            return self._get_default_prompts()

    def _get_default_prompts(self) -> Dict:
        """Fallback default prompts"""

        return {
            "meta": {"version": "1.0.0"},
            "core_prompts": {
                "welcome": {"prompt": "أهلاً بيك يا {child_name}!"}
            },
            "feedback": {
                "default": "أحسنت! استمر في التدريب"
            }
        }

    def set_emotional_state(self, state: str):
        """Set current emotional state"""

        valid_states = [
            "very_happy",
            "happy",
            "neutral",
            "tired",
            "frustrated",
            "anxious",
        ]

        if state in valid_states:
            self.emotional_state = state

    def get_emotional_prefix(self) -> str:
        """Get emotional state prefix"""

        state_config = self.prompts.get(
            "emotional_state_system",
            {}
        ).get("states", {})

        state_data = state_config.get(
            self.emotional_state,
            {}
        )

        return state_data.get("prefix", "")

    def get_emotional_support_prompt(self, emotion: str) -> str:
        """Get emotional support prompt"""

        support_messages = {
            "frustrated": "حاول مرة تانية بهدوء.",
            "anxious": "خد وقتك في الكلام.",
            "tired": "ممكن نرتاح شوية ونكمل.",
            "happy": "واضح إنك متحمس النهاردة.",
            "neutral": "كمل بنفس التركيز."
        }

        return support_messages.get(
            emotion,
            "كمل بهدوء."
        )

    def get_emotional_emoji(self) -> str:
        """Return emotional emoji"""

        emoji_map = {
            "very_happy": "",
            "happy": "",
            "neutral": "",
            "tired": "",
            "frustrated": "",
            "anxious": ""
        }

        return emoji_map.get(
            self.emotional_state,
            ""
        )

    def render_prompt(
        self,
        prompt_key: str,
        variables: Dict[str, Any] = None
    ) -> str:
        """Render prompt with variables"""

        if variables is None:
            variables = {}

        keys = prompt_key.split(".")
        data = self.prompts

        for key in keys:
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return "أهلاً بيك!"

        if isinstance(data, dict):
            prompt_text = data.get("prompt", str(data))
        else:
            prompt_text = str(data)

        for key, value in variables.items():
            placeholder = f"{{{key}}}"

            if placeholder in prompt_text:
                prompt_text = prompt_text.replace(
                    placeholder,
                    str(value)
                )

        return prompt_text

    def get_feedback_prompt(self, feedback_type: str) -> str:
        """Get feedback prompt by type"""

        feedbacks = self.prompts.get("feedback", {})

        return feedbacks.get(
            feedback_type,
            feedbacks.get("default", "أحسنت")
        )

    def generate_realtime_feedback(
        self,
        accuracy: float,
        stuttering_detected: bool = False,
        articulation_error: bool = False
    ) -> str:
        """Generate realtime feedback"""

        if stuttering_detected:
            return "خد وقتك في الكلام وحاول بهدوء."

        elif articulation_error:
            return "حاول تنطق الصوت بشكل أوضح."

        elif accuracy >= 85:
            return "واضح إنك بتتحسن جدًا."

        elif accuracy >= 60:
            return "كويس، كمل بنفس التركيز."

        elif accuracy >= 40:
            return "أنت قريب توصل للنطق الصح."

        else:
            return "حاول مرة كمان بهدوء."

    def merge_with_analysis(
        self,
        prompt: str,
        analysis_result: Dict[str, Any],
        acoustic_features: Dict[str, float]
    ) -> str:
        """
        Enhance prompt dynamically using speech analysis
        and let Gemini generate the final response naturally.
        """

        accuracy = analysis_result.get("accuracy", 0)

        exercise_correct = analysis_result.get(
            "exercise_correct",
            False
        )

        repetition_count = analysis_result.get(
            "repetition_count",
            0
        )

        pause_count = analysis_result.get(
            "pause_count",
            0
        )

        prolongation_count = analysis_result.get(
            "prolongation_count",
            0
        )

        stuttering_type = analysis_result.get(
            "stuttering_type",
            "none"
        )

        severity = analysis_result.get(
            "severity",
            "unknown"
        )

        target_phoneme = analysis_result.get(
            "target_phoneme",
            ""
        )

        mean_f0 = acoustic_features.get("mean_f0", 0)
        jitter = acoustic_features.get("jitter", 0)
        shimmer = acoustic_features.get("shimmer", 0)
        hnr = acoustic_features.get("hnr", 0)
        energy_dev = acoustic_features.get("energy_dev", 0)

        if accuracy >= 85:
            performance_level = "excellent"

        elif accuracy >= 60:
            performance_level = "good"

        elif accuracy >= 40:
            performance_level = "needs_improvement"

        else:
            performance_level = "poor"

        if mean_f0 > 350 or jitter > 0.03 or shimmer > 0.05:
            emotional_hint = "child might be anxious or stressed"

        elif mean_f0 < 220 and energy_dev < 0.1:
            emotional_hint = "child might be tired or low energy"

        elif hnr > 15 and energy_dev < 0.15:
            emotional_hint = "child sounds confident and comfortable"

        else:
            emotional_hint = "child is in a normal state"

        enhanced_prompt = f"""

أنت معالج نطق للأطفال تتحدث باللهجة المصرية الطبيعية.

بناءً على نتائج التحليل التالية، أنشئ رسالة قصيرة ولطيفة للطفل.

نتائج التحليل:
- دقة النطق: {accuracy}%
- التمرين صحيح: {'نعم' if exercise_correct else 'لا'}
- الحرف المستهدف: {target_phoneme}

تفاصيل الأداء:
- مستوى الأداء: {performance_level}
- عدد التكرارات: {repetition_count}
- عدد التوقفات: {pause_count}
- عدد الإطالات: {prolongation_count}
- نوع التلعثم: {stuttering_type}
- شدة المشكلة: {severity}

المؤشرات الصوتية:
- Mean F0: {mean_f0}
- Jitter: {jitter}
- Shimmer: {shimmer}
- HNR: {hnr}

الحالة المتوقعة:
{emotional_hint}

تعليمات مهمة:
- الرد يكون باللهجة المصرية البسيطة.
- الرد قصير وطبيعي.
- لا تستخدم Emoji نهائيًا.
- لا تكرر نفس الجمل كل مرة.
- لا تجعل الرد روبوتي أو محفوظ.
- لا تبدأ دائمًا بـ "أحسنت" أو "ممتاز".
- لو الأداء ضعيف كن هادئ ومشجع.
- لو الأداء ممتاز شجع الطفل بشكل طبيعي.
- لو الطفل متوتر حاول تطمنه بهدوء.
- استخدم أسلوب أخصائي تخاطب حقيقي.

اكتب الرد النهائي فقط.
"""

        return enhanced_prompt

    def reset_context(self):
        """Reset child context"""

        self.child_context = {}
        self.emotional_state = "neutral"


# Singleton instance
prompt_manager = PromptManager()
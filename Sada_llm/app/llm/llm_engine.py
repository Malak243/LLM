"""
LLM Engine - Gemini Official SDK Version
"""

from typing import Dict, Any, Optional

import google.generativeai as genai

from app.config.settings import llm_settings
from app.llm.prompt_manager import prompt_manager


class LLMEngine:

    def __init__(self):

        self.settings = llm_settings
        self.prompt_manager = prompt_manager
        self.model = None

        try:

            genai.configure(
                api_key=self.settings.GOOGLE_API_KEY
            )

            self.model = genai.GenerativeModel(
                self.settings.GOOGLE_MODEL
            )

            print("✅ Gemini Connected Successfully")
            print(f"🔥 Active Model: {self.settings.GOOGLE_MODEL}")

        except Exception as e:

            print("❌ Gemini Connection Error")
            print(str(e))

    def _call_llm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> str:

        if not self.model:
            return "الموديل مش متوصل"

        try:

            full_prompt = f"""
{system_prompt or '''
أنت أخصائي تخاطب للأطفال.

تتحدث باللهجة المصرية الطبيعية جدًا.

قواعد مهمة جدًا:
- كل رد يكون مختلف تمامًا.
- لا تستخدم ردود محفوظة.
- لا تكرر نفس البداية.
- لا تستخدم Emoji.
- الكلام يكون طبيعي جدًا.
- الرد قصير من سطر إلى ٣ سطور.
- تصرف كإنسان حقيقي.
- غيّر الأسلوب في كل مرة.
'''}

{prompt}
"""

            response = self.model.generate_content(
                full_prompt
            )

            text = response.text

            if text:
                return text.strip()

            return "حاول مرة تانية"

        except Exception as e:

            print("❌ LLM ERROR")
            print(str(e))

            return f"حصل خطأ في الموديل: {str(e)}"

    def generate_feedback(

        self,
        analysis_result: Dict[str, Any],
        accuracy: float,
        exercise_correct: bool = False,
        emotional_state: str = "neutral"

    ) -> str:

        self.prompt_manager.set_emotional_state(
            emotional_state
        )

        acoustic_features = analysis_result.get(
            "acoustic_features",
            {}
        )

        dynamic_prompt = self.prompt_manager.merge_with_analysis(

            prompt="Generate feedback",

            analysis_result=analysis_result,

            acoustic_features=acoustic_features

        )

        print("🔥 PROMPT SENT TO GEMINI:")
        print(dynamic_prompt)

        response = self._call_llm(dynamic_prompt)

        print("✅ GEMINI RESPONSE:")
        print(response)

        return response

    def generate_therapy_prompt(

        self,
        problem_type: str,
        activity_name: str,
        variables: Dict[str, Any],
        emotional_state: str = "neutral"

    ) -> str:

        prompt = f"""

أنشئ تعليمات علاج تخاطب لطفل.

نوع المشكلة:
{problem_type}

اسم النشاط:
{activity_name}

الحالة العاطفية:
{emotional_state}

البيانات:
{variables}

اجعل الكلام باللهجة المصرية الطبيعية.
"""

        return self._call_llm(prompt)

    def generate_session_welcome(

        self,
        child_name: str,
        day_name: str = None,
        previous_activity: str = None,
        total_stars: int = 0,
        emotional_state: str = "neutral"

    ) -> str:

        prompt = f"""

أنشئ رسالة ترحيب لطفل.

اسم الطفل:
{child_name}

عدد النجوم:
{total_stars}

الحالة:
{emotional_state}

اجعل الرسالة طبيعية وغير مكررة.
"""

        return self._call_llm(prompt)

    def generate_session_summary(

        self,
        child_name: str,
        activities_count: int,
        stars_earned: int,
        best_achievement: str = None

    ) -> str:

        prompt = f"""

أنشئ ملخص جلسة لطفل.

عدد الأنشطة:
{activities_count}

عدد النجوم:
{stars_earned}

أفضل إنجاز:
{best_achievement}

استخدم أسلوب لطيف باللهجة المصرية.
"""

        return self._call_llm(prompt)

    def generate_farewell(

        self,
        child_name: str,
        emotional_state: str = "neutral"

    ) -> str:

        prompt = f"""

أنشئ رسالة وداع لطفل.

اسم الطفل:
{child_name}

الحالة:
{emotional_state}

لا تجعل الرسالة مكررة.
"""

        return self._call_llm(prompt)


# Singleton instance
llm_engine = LLMEngine()
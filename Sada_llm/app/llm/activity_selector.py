"""
Activity Selector - Chooses appropriate activities based on child's performance
"""

from typing import Dict, Any, List, Optional
from app.llm.llm_engine import llm_engine


class ActivitySelector:
    """Selects and adapts activities based on child's progress"""
    
    # Activity bank by level and problem type
    ACTIVITIES = {
        "articulation": {
            "isolation": [
                "كرر الحرف {letter} 5 مرات",
                "قل الحرف {letter} مع حركات مختلفة (أ، و، ي)",
                "لعبة: ابحث عن الصور التي تبدأ بـ {letter}",
                "غني أغنية بسيطة تحتوي على الحرف {letter}"
            ],
            "syllable": [
                "قل المقطع {syllable} 3 مرات",
                "أكمل الكلمة: {syllable}__",
                "صل المقاطع لتكوين كلمة: {syllable1} + {syllable2}",
                "قل الجملة: أنا أحب {syllable}"
            ],
            "word": [
                "كرر كلمة {word} بوضوح",
                "استخدم كلمة {word} في جملة مفيدة",
                "صف الصورة التي تمثل كلمة {word}",
                "لعبة: ابحث عن كلمة {word} في القصة"
            ],
            "sentence": [
                "كرر الجملة: {sentence}",
                "أجب عن السؤال: {question}",
                "صف ما يحدث في الصورة: {sentence_template}",
                "أكمل القصة: بدأت الجملة بـ {sentence_start}"
            ]
        },
        
        "fluency": {
            "isolation": [
                "قل الأصوات ببطء وتؤدة: {phonemes}",
                "تمرين التنفس: خذ نفساً عميقاً ثم قل 'آآآ'",
                "قل الكلمة ببطء مع إطالة الحرف الأول: {slow_word}",
                "تمرين التنغيم: غير نغمة صوتك أثناء قول {sound}"
            ],
            "syllable": [
                "قل المقطع {syllable} بتؤدة",
                "تقسيم المقطع: {syllable} = {part1} + {part2}",
                "تمرين الإيقاع: دق إيقاع المقطع {syllable}",
                "قل المقطع 3 مرات بسرعات مختلفة"
            ],
            "word": [
                "قل الكلمة {word} ثم خذ نفساً",
                "قسم الكلمة إلى مقاطع: {word} = {syllables}",
                "قل الكلمة في جملة قصيرة جداً",
                "تمرين: قل الكلمة مع حركة اليد"
            ],
            "sentence": [
                "قل الجملة {sentence} بتؤدة",
                "قسم الجملة إلى أجزاء وتوقف قليلاً بين كل جزء",
                "تمرين التنفس: خذ نفساً عميقاً قبل كل جملة",
                "كرر الجملة 3 مرات، في كل مرة زد السرعة قليلاً"
            ]
        }
    }
    
    def select_activity(
        self,
        problem_type: str,
        level: str,
        target_letter: Optional[str] = None,
        target_word: Optional[str] = None,
        target_sentence: Optional[str] = None,
        adaptation_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Select an appropriate activity for the child
        
        Returns:
            Dict with activity text and metadata
        """
        
        # Get activities for problem type and level
        activities = self.ACTIVITIES.get(problem_type, {}).get(level, [])
        
        if not activities:
            # Fallback activity
            return {
                "text": "كرر التمرين مع التركيز على النطق الصحيح",
                "type": "repetition",
                "difficulty": "normal"
            }
        
        # Apply adaptation if provided
        if adaptation_data and adaptation_data.get("error_pattern"):
            activities = self._adapt_activities(
                activities,
                adaptation_data,
                problem_type,
                level
            )
        
        # Select activity (could be based on performance, random, or LLM)
        selected_index = self._select_activity_index(adaptation_data)
        activity_text = activities[selected_index % len(activities)]
        
        # Fill placeholders
        activity_text = self._fill_activity_placeholders(
            activity_text,
            target_letter=target_letter,
            target_word=target_word,
            target_sentence=target_sentence
        )
        
        return {
            "text": activity_text,
            "type": self._extract_activity_type(activity_text),
            "difficulty": level,
            "index": selected_index
        }
    
    def _adapt_activities(
        self,
        activities: List[str],
        adaptation_data: Dict,
        problem_type: str,
        level: str
    ) -> List[str]:
        """Adapt activities based on error patterns"""
        
        error_pattern = adaptation_data.get("error_pattern", "")
        
        if problem_type == "articulation":
            if error_pattern == "substitution":
                # Add more focused repetition activities
                focused = [
                    "ركز على وضع اللسان أثناء نطق الحرف",
                    "انظر في المرآة أثناء النطق",
                    "كرر الحرف ببطء مع مراقبة حركة الفم"
                ]
                activities = focused + activities
            
            elif error_pattern == "distortion":
                # Add articulation exercises
                focused = [
                    "تمرين: ضع طرف لسانك خلف الأسنان العلوية",
                    "انفخ الهواء برفق أثناء النطق",
                    "استخدم قطعة حلوى لتوجيه اللسان"
                ]
                activities = focused + activities
        
        elif problem_type == "fluency":
            if error_pattern == "repetition":
                focused = [
                    "تمرين التنفس العميق قبل البدء",
                    "قل كل كلمة بتؤدة وتوقف قليلاً بعدها",
                    "استخدم إيقاعاً بطيئاً ومنظماً"
                ]
                activities = focused + activities
            
            elif error_pattern == "block":
                focused = [
                    "تمرين: ابدأ بصوت خفيف جداً ثم ارفعه",
                    "قل الحرف الأول بهدوء",
                    "حرك يدك أثناء النطق لتخفيف التوتر"
                ]
                activities = focused + activities
        
        return activities
    
    def _select_activity_index(self, adaptation_data: Optional[Dict]) -> int:
        """Select activity index based on performance"""
        if adaptation_data and adaptation_data.get("repetition_count", 0) > 2:
            # If many repetitions, change activity type
            return 2  # Choose different activity
        return 0
    
    def _fill_activity_placeholders(
        self,
        text: str,
        target_letter: Optional[str] = None,
        target_word: Optional[str] = None,
        target_sentence: Optional[str] = None
    ) -> str:
        """Fill placeholders in activity text"""
        
        filled = text
        
        if target_letter:
            filled = filled.replace("{letter}", target_letter)
            filled = filled.replace("{phonemes}", target_letter)
            filled = filled.replace("{sound}", target_letter)
        
        if target_word:
            filled = filled.replace("{word}", target_word)
            # Generate syllable breakdown
            if len(target_word) >= 2:
                syllables = self._split_into_syllables(target_word)
                filled = filled.replace("{syllable}", syllables[0] if syllables else target_word)
                filled = filled.replace("{syllable1}", syllables[0] if len(syllables) > 0 else target_word)
                filled = filled.replace("{syllable2}", syllables[1] if len(syllables) > 1 else "")
                filled = filled.replace("{syllables}", " + ".join(syllables))
            filled = filled.replace("{slow_word}", target_word[0] + "..." + target_word[1:] if len(target_word) > 1 else target_word)
        
        if target_sentence:
            filled = filled.replace("{sentence}", target_sentence)
            # Generate question from sentence
            filled = filled.replace("{question}", f"ماذا قال الشخص؟")
            filled = filled.replace("{sentence_template}", target_sentence)
            filled = filled.replace("{sentence_start}", target_sentence[:10] + "..." if len(target_sentence) > 10 else target_sentence)
        
        # Clean up any remaining placeholders
        import re
        filled = re.sub(r'\{[^}]+\}', 'تمرين', filled)
        
        return filled
    
    def _split_into_syllables(self, word: str) -> List[str]:
        """Simple syllable splitting for Arabic"""
        # This is a simplified version
        syllables = []
        current = ""
        
        # Arabic vowels and consonant clusters
        vowels = "اوي"
        
        for char in word:
            current += char
            if char in vowels and len(current) > 1:
                syllables.append(current)
                current = ""
        
        if current:
            syllables.append(current)
        
        return syllables if syllables else [word]
    
    def _extract_activity_type(self, activity_text: str) -> str:
        """Extract activity type from text"""
        if "كرر" in activity_text or "repeat" in activity_text.lower():
            return "repetition"
        if "لعبة" in activity_text or "game" in activity_text.lower():
            return "game"
        if "تمرين" in activity_text or "exercise" in activity_text.lower():
            return "exercise"
        if "غني" in activity_text or "sing" in activity_text.lower():
            return "singing"
        return "practice"


# Singleton instance
activity_selector = ActivitySelector()
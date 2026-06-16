"""
Prompt Builder - Builds prompts for the LLM based on child's data
"""

from typing import Dict, Any, Optional


def build_therapy_prompt(
    child_data: Dict[str, Any]
) -> str:

    """
    Builds a prompt for the LLM
    with strict tone control
    based on accuracy.
    """

    # ========================================================
    # استخراج البيانات الأساسية
    # ========================================================

    accuracy = child_data.get(
        'accuracy',
        0
    )

    exercise_correct = child_data.get(
        'exercise_correct',
        True
    )

    error_type = child_data.get(
        'error_type'
    )

    target_phoneme = child_data.get(
        'target_phoneme',
        ''
    )

    repetition_count = child_data.get(
        'repetition_count',
        0
    )

    pause_count = child_data.get(
        'pause_count',
        0
    )

    prolongation_count = child_data.get(
        'prolongation_count',
        0
    )

    severity = child_data.get(
        'severity',
        'خفيفة'
    )

    problem = child_data.get(
        'problem',
        'غير محدد'
    )

    stuttering_type = child_data.get(
        'stuttering_type',
        ''
    )

    acoustic_features = child_data.get(
        'acoustic_features',
        {}
    )

    hnr = acoustic_features.get(
        'hnr',
        0
    )

    # ========================================================
    # التحكم المنطقي في الرد
    # ========================================================

    if accuracy >= 85:

        category = "excellent"

        allowed_praise = """
استخدم مدح قوي وطبيعي مثل:
- ممتاز
- برافو
- أداء رائع
- ما شاء الله
"""

        prohibited = """
ممنوع التقليل من الأداء.
"""

        tone = """
متحمس وحماسي.
"""

        example = """
مثال:
"ما شاء الله،
نطقك ممتاز جداً،
كمل كده."
"""

    elif accuracy >= 70:

        category = "good"

        allowed_praise = """
استخدم مدح معتدل مثل:
- أحسنت
- كويس
- قربت
"""

        prohibited = """
لا تستخدم مدح مبالغ فيه
مثل:
- رائع جداً
- مذهل
"""

        tone = """
إيجابي مع تلميح بسيط للتحسين.
"""

        example = """
مثال:
"أحسنت،
جرب تقول الحرف
بوضوح أكتر."
"""

    elif accuracy >= 50:

        category = "average"

        allowed_praise = """
استخدم تشجيع بسيط فقط
بدون مدح قوي.
"""

        prohibited = """
ممنوع استخدام:
- ممتاز
- برافو
- رائع
- ما شاء الله
"""

        tone = """
داعم وهادئ
مع تشجيع للمحاولة مرة أخرى.
"""

        example = """
مثال:
"قربت،
جرب تقولها
تاني بهدوء."
"""

    else:

        category = "poor"

        allowed_praise = """
ممنوع تماماً أي مدح
أو وصف إيجابي للأداء.

المطلوب فقط:
- تهدئة الطفل
- دعمه نفسياً
- تشجيعه على المحاولة مرة أخرى
"""

        prohibited = """
ممنوع استخدام أي كلمة مدح مثل:

- برافو
- شاطر
- ممتاز
- جميل
- كويس
- رائع
- فخور بيك
- أحسنت
- محاولة جميلة
- محاولة كويسة
- أداء حلو
- جامد
- عظيم

إذا استخدمت أي كلمة
من هذه الكلمات
فالرد يعتبر خاطئ.
"""

        tone = """
هادئ جداً وحنون
ويركز على المحاولة فقط
وليس الأداء.
"""

        example = """
مثال:
"مش مشكلة،
خد نفس بهدوء
وجرب الحرف
مرة تانية معايا."

أو:

"معليش،
قولها بالراحة
وإحنا هنجرب تاني."
"""

    # ========================================================
    # بناء السياق الإضافي
    # ========================================================

    extra = ""

    if repetition_count > 2:

        extra += f"""

- الطفل كرر المحاولة
{repetition_count} مرات.

- هذا يدل على أنه
يبذل مجهوداً.
"""

    if pause_count >= 2:

        extra += """

- يوجد تردد أو توقف
أثناء الكلام.
"""

    if prolongation_count >= 2:

        extra += """

- يوجد إطالة
في بعض الأصوات.
"""

    if (
        stuttering_type
        and stuttering_type
        not in ["none", None]
    ):

        extra += f"""

- يوجد تلعثم
من نوع:
{stuttering_type}

- اطلب منه
أن يتكلم ببطء.
"""

    if error_type:

        extra += f"""

- يوجد خطأ
من نوع:
{error_type}

- الحرف المستهدف:
{target_phoneme}

- لا تركز على الخطأ،
بل اطلب منه
إعادة المحاولة بهدوء.
"""

    if severity in ['severe', 'شديد']:

        extra += """

- الحالة شديدة.

- كن هادئاً جداً
ولا تظهر أي إحباط.
"""

    if hnr and hnr < 10:

        extra += """

- الطفل يبدو متوتراً
أثناء الكلام.

- طمئنه واطلب منه
أن يأخذ نفساً.
"""

    # ========================================================
    # البرومبت النهائي
    # ========================================================

    prompt = f"""

أنت أخصائي تخاطب أطفال
حقيقي ومحترف.

تتحدث باللهجة المصرية الطبيعية.

ردك يجب أن يكون:
- طبيعي جداً
- قصير
- جملة أو جملتين فقط

### بيانات الحالة:

- المشكلة:
{problem}

- الدقة:
{accuracy}%

- مستوى الأداء:
{category}

- التمرين:
{"صحيح" if exercise_correct else "به أخطاء"}

- شدة الحالة:
{severity}

{extra}

### قواعد الرد المهمة جداً:

- المديح المسموح:
{allowed_praise}

- المديح الممنوع:
{prohibited}

- النبرة المطلوبة:
{tone}

- نمط الرد:
{example}

### تعليمات صارمة جداً:

إذا كانت الدقة أقل من 50%:

- ممنوع تماماً مدح الأداء
- ممنوع وصف المحاولة بأنها جيدة
- ممنوع استخدام كلمات مثل:
  شاطر - ممتاز - كويس - جميل
  برافو - رائع - فخور بيك

- ركز فقط على:
  - التهدئة
  - الدعم النفسي
  - إعادة المحاولة

- أي مدح يعتبر
رد غير صحيح.

### تعليمات إضافية:

- لا تكرر نفس بداية الرد دائماً.
- لا تذكر النسب الرقمية.
- لا تستخدم Emoji.
- اجعل الرد طبيعي جداً
وكأنه أخصائي تخاطب حقيقي.

### اكتب الرد النهائي فقط:

"""

    return prompt


# ============================================================
# نسخة مبسطة
# ============================================================

def build_simple_prompt(
    accuracy: int,
    exercise_correct: bool,
    error_type: str = None,
    target_phoneme: str = ""
) -> str:

    if accuracy >= 85:

        return f"""
دقة الطفل {accuracy}%.
اكتب رد مدح قوي
بالعامية المصرية.
"""

    elif accuracy >= 70:

        return f"""
دقة الطفل {accuracy}%.
اكتب رد تشجيع معتدل
بدون مبالغة.
"""

    elif accuracy >= 50:

        return f"""
دقة الطفل {accuracy}%.
اكتب رد داعم
مع تشجيع بسيط فقط.
"""

    else:

        return f"""
دقة الطفل {accuracy}%.

ممنوع تماماً أي مدح.

لا تستخدم:
- شاطر
- ممتاز
- كويس
- برافو
- رائع

اكتب رد هادئ
يشجع الطفل
على إعادة المحاولة فقط.
"""
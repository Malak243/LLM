"""
SADA LLM API - خدمة Gemini لتوليد الردود العلاجية
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import google.generativeai as genai

from app.tts_service import text_to_speech

# ============================================================
# إعدادات Gemini
# ============================================================

GEMINI_API_KEY = "__"

genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-3.1-flash-lite"

model = genai.GenerativeModel(MODEL_NAME)

# ============================================================
# Models
# ============================================================

class AcousticFeatures(BaseModel):
    mean_f0: Optional[float] = None
    jitter: Optional[float] = None
    shimmer: Optional[float] = None
    hnr: Optional[float] = None
    energy_dev: Optional[float] = None


class TherapyRequest(BaseModel):
    child_message: Optional[str] = None
    problem: Optional[str] = None
    accuracy: Optional[int] = 0
    exercise_correct: Optional[bool] = True
    repetition_count: Optional[int] = 0
    severity: Optional[str] = None
    acoustic_features: Optional[
        AcousticFeatures
    ] = None


class TherapyResponse(BaseModel):
    reply: str
    emotional_state: str
    needs_intervention: bool
    confidence_score: float
    audio_file: str | None = None


# ============================================================
# Prompt Builder
# ============================================================

def build_therapy_prompt(
    request: TherapyRequest
):

    child_msg = (
        request.child_message
        or "الطفل كان يتدرب على النطق"
    )

    accuracy = request.accuracy or 0

    # ========================================================
    # التحكم المنطقي في الرد
    # ========================================================

    if accuracy >= 85:

        instructions = """
- استخدم مدح قوي وطبيعي
- يمكنك قول:
  برافو
  ممتاز
  أداء رائع
"""

    elif accuracy >= 70:

        instructions = """
- استخدم تشجيع معتدل
- لا تبالغ في المدح
"""

    elif accuracy >= 50:

        instructions = """
- استخدم تشجيع بسيط فقط
- لا تستخدم مدح قوي
"""

    else:

        instructions = """
- ممنوع تماماً أي مدح
- ممنوع استخدام:
  برافو
  شاطر
  ممتاز
  كويس
  رائع
  جميل
  فخور بيك
  أحسنت

- المطلوب فقط:
  تهدئة الطفل
  وتشجيعه على المحاولة مرة أخرى
"""

    # ========================================================
    # التحليل الصوتي
    # ========================================================

    analysis = ""

    if request.acoustic_features:

        analysis = f"""
دقة النطق:
{accuracy}%

نوع المشكلة:
{request.problem or 'غير محدد'}

عدد التكرارات:
{request.repetition_count}

شدة المشكلة:
{request.severity or 'خفيفة'}

HNR:
{request.acoustic_features.hnr}
"""

    # ========================================================
    # البرومبت النهائي
    # ========================================================

    prompt = f"""
أنت أخصائي تخاطب أطفال
محترف.

تحدث باللهجة المصرية الطبيعية.

ما قاله الطفل:
{child_msg}

{analysis}

================================================

تعليمات الرد:

{instructions}

================================================

قواعد إضافية:

- الرد يكون قصير
- الرد يكون طبيعي جداً
- لا تستخدم Emoji
- لا تذكر النسب الرقمية
- الرد يكون جملة أو جملتين فقط

================================================

إذا كانت الدقة أقل من 50%:
أي مدح يعتبر رد خاطئ.

================================================

اكتب الرد النهائي فقط:
"""

    return prompt


# ============================================================
# فلترة الرد بعد Gemini
# ============================================================

def filter_low_accuracy_reply(
    reply: str,
    accuracy: int
):

    if accuracy >= 50:
        return reply

    banned_words = [
        "برافو",
        "شاطر",
        "ممتاز",
        "كويس",
        "رائع",
        "جميل",
        "فخور",
        "أحسنت",
        "عظيم",
        "جامد"
    ]

    for word in banned_words:

        reply = reply.replace(
            word,
            ""
        )

    reply = " ".join(
        reply.split()
    )

    # لو الرد باظ بعد التنظيف
    if len(reply.strip()) < 10:

        reply = (
            "مش مشكلة، "
            "خد نفس بهدوء "
            "وجرب مرة تانية."
        )

    return reply


# ============================================================
# Emotional Analysis
# ============================================================

def analyze_emotional_state(
    request: TherapyRequest
):

    features = (
        request.acoustic_features
    )

    if not features:
        return "neutral", 0.6

    if (
        features.hnr
        and features.hnr < 10
    ):

        return "anxious", 0.75

    if (
        request.repetition_count
        and request.repetition_count > 3
    ):

        return "struggling", 0.8

    return "calm", 0.65


# ============================================================
# FastAPI App
# ============================================================

app = FastAPI(
    title="SADA Therapeutic LLM API",
    version="1.0.0"
)


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/")

def root():

    return {
        "message": "SADA API شغالة",
        "model": MODEL_NAME,
        "endpoints": [
            "/therapy",
            "/audio",
            "/health",
            "/docs"
        ]
    }


# ============================================================
# Therapy Endpoint
# ============================================================

@app.post(
    "/therapy",
    response_model=TherapyResponse
)

async def therapy_endpoint(
    request: TherapyRequest
):

    try:

        # ====================================================
        # Build Prompt
        # ====================================================

        prompt = build_therapy_prompt(
            request
        )

        print(
            "\n========== PROMPT ==========\n"
        )

        print(prompt)

        # ====================================================
        # Gemini Response
        # ====================================================

        response = model.generate_content(
            prompt
        )

        therapy_reply = (
            response.text.strip()
        )

        print(
            "\n========== GEMINI REPLY ==========\n"
        )

        print(therapy_reply)

        # ====================================================
        # فلترة الرد
        # ====================================================

        therapy_reply = (
            filter_low_accuracy_reply(
                therapy_reply,
                request.accuracy or 0
            )
        )

        # ====================================================
        # Text To Speech
        # ====================================================

        audio_path = await text_to_speech(
            therapy_reply
        )

        # ====================================================
        # Audio URL
        # ====================================================

        audio_url = (
            f"http://127.0.0.1:8000/audio?path={audio_path}"
        )

        # ====================================================
        # Emotional State
        # ====================================================

        emotional_state, confidence = (
            analyze_emotional_state(
                request
            )
        )

        needs_intervention = (
            emotional_state in [
                "anxious",
                "struggling"
            ]
        )

        # ====================================================
        # Response
        # ====================================================

        return TherapyResponse(
            reply=therapy_reply,
            emotional_state=emotional_state,
            needs_intervention=needs_intervention,
            confidence_score=confidence,
            audio_file=audio_url
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# Audio Endpoint
# ============================================================

@app.get("/audio")

async def get_audio(path: str):

    return FileResponse(
        path=path,
        media_type="audio/mpeg"
    )


# ============================================================
# Health Endpoint
# ============================================================

@app.get("/health")

def health():

    return {
        "status": "healthy",
        "model": MODEL_NAME
    }


# ============================================================
# Run Server
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )

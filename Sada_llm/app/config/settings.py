"""
LLM Configuration Settings - Gemini Configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()


class LLMSettings:
    """LLM configuration settings"""

    # ==============================
    # Gemini Settings
    # ==============================

    GOOGLE_API_KEY = os.getenv(
        "GOOGLE_API_KEY",
        "AIzaSyDFmgYS9C_u1pHBcEtuJXgBoqD9PoRsGWk"
    )

    GOOGLE_MODEL = os.getenv(
        "GOOGLE_MODEL",
        "gemini-3.1-flash-lite"
    )
    
    # ==============================
    # Generation Settings
    # ==============================

    TEMPERATURE = 1.8

    MAX_TOKENS = 120

    FEEDBACK_MAX_LENGTH = 300

    USE_ARABIC_PROMPTS = True

    # ==============================
    # Prompt File
    # ==============================

    PROMPT_FILE = os.path.join(
        os.path.dirname(__file__),
        "prompt.json"
    )

    def __init__(self):

        print("===================================")
        print("🚀 SADA AI SETTINGS LOADED")
        print("===================================")

        print(f"🤖 Model: {self.GOOGLE_MODEL}")

        if self.GOOGLE_API_KEY:

            print("✅ Gemini API Key Loaded")

            print(
                f"🔑 Key Preview: "
                f"{self.GOOGLE_API_KEY[:15]}..."
            )

        else:

            print("❌ Gemini API Key Missing")

        print("===================================")

    def is_google_available(self) -> bool:
        """Check Gemini availability"""

        return bool(self.GOOGLE_API_KEY)

    def get_active_model(self) -> str:
        """Return active model"""

        return self.GOOGLE_MODEL

    def load_prompts(self):
        """Dummy prompt loader"""

        return {}

    def get_prompt(
        self,
        category: str,
        key: str,
        default: str = None
    ) -> str:

        if default:
            return default

        return "حاول مرة تانية"


# Singleton instance
llm_settings = LLMSettings()
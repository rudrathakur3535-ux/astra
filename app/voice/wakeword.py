import re
from typing import Tuple, Optional
from app.config import settings
from app.utils.logger import logger

class WakeWordDetector:
    """Wake word trigger detection and phrase extraction."""

    def __init__(self, wake_word: Optional[str] = None):
        self.wake_word = (wake_word or settings.WAKE_WORD).strip().lower()

    def check_wake_word(self, transcribed_text: str) -> Tuple[bool, str]:
        """Checks if transcribed text contains the wake word and extracts post-wake word prompt.
        
        Args:
            transcribed_text: Text from STT transcription.
            
        Returns:
            Tuple[bool, str]: (is_wake_word_detected, extracted_prompt)
        """
        text_clean = re.sub(r"[^\w\s]", "", transcribed_text.lower()).strip()
        wake_clean = re.sub(r"[^\w\s]", "", self.wake_word).strip()

        if not text_clean:
            return False, ""

        # Check exact or fuzzy matching for wake word
        if wake_clean in text_clean or "astra" in text_clean or "hey astra" in text_clean:
            logger.info(f"Wake word detected in input: '{transcribed_text}'")

            # Extract user prompt following wake word
            pattern = re.compile(re.escape(wake_clean), re.IGNORECASE)
            parts = pattern.split(transcribed_text, maxsplit=1)

            extracted_prompt = ""
            if len(parts) > 1 and parts[1].strip():
                extracted_prompt = parts[1].strip()
            elif "astra" in text_clean:
                # Fallback splitting by "astra"
                parts = re.split(r"astra", transcribed_text, flags=re.IGNORECASE, maxsplit=1)
                if len(parts) > 1 and parts[1].strip():
                    extracted_prompt = parts[1].strip()

            return True, extracted_prompt

        return False, ""

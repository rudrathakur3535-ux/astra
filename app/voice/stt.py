import io
from typing import Optional
import numpy as np
import soundfile as sf
from openai import OpenAI
import speech_recognition as sr
from app.config import settings
from app.utils.logger import logger

class WhisperSTT:
    """Multi-provider Speech-to-Text transcriber supporting OpenAI Whisper and Free SpeechRecognition fallback."""

    def __init__(self, api_key: Optional[str] = None):
        from app.security.secret_manager import SecretManager
        sm = SecretManager()
        self.api_key = api_key or sm.get_secret("OPENAI_API_KEY") or settings.OPENAI_API_KEY
        self.client: Optional[OpenAI] = None
        self.sr_recognizer = sr.Recognizer()
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initializes API client for audio transcription if valid OpenAI key is present."""
        if not self.api_key or not self.api_key.startswith("sk-") or self.api_key.startswith("sk_"):
            logger.info("OpenAI API key unavailable. Using free SpeechRecognition STT engine.")
            self.client = None
            return

        try:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("OpenAI Whisper STT client initialized.")
        except Exception as e:
            logger.info(f"OpenAI Whisper client initialization skipped ({e}). Using SpeechRecognition fallback.")
            self.client = None

    def transcribe(self, audio_data: np.ndarray, sample_rate: int = settings.SAMPLE_RATE) -> str:
        """Transcribes raw numpy float32 audio array into text.
        
        Args:
            audio_data: Float32 numpy audio waveform array.
            sample_rate: Sampling frequency in Hz.
            
        Returns:
            str: Transcribed text string.
        """
        if len(audio_data) == 0:
            return ""

        # Convert numpy audio array into WAV format in-memory BytesIO buffer
        byte_io = io.BytesIO()
        byte_io.name = "audio.wav"
        sf.write(byte_io, audio_data, sample_rate, format="WAV", subtype="PCM_16")
        byte_io.seek(0)

        # 1. Try OpenAI Whisper API if client is available
        if self.client:
            try:
                logger.debug("Sending audio clip to OpenAI Whisper API...")
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=byte_io,
                    language="en"
                )
                transcribed_text = response.text.strip()
                if transcribed_text:
                    logger.info(f"Whisper Transcription: '{transcribed_text}'")
                    return transcribed_text
            except Exception as e:
                logger.debug(f"OpenAI Whisper transcription skipped: {e}. Trying SpeechRecognition...")

        # 2. Fallback to free SpeechRecognition engine
        try:
            byte_io.seek(0)
            with sr.AudioFile(byte_io) as source:
                audio_file_data = self.sr_recognizer.record(source)
                text = self.sr_recognizer.recognize_google(audio_file_data)
                clean_text = text.strip()
                if clean_text:
                    logger.info(f"SpeechRecognition STT Output: '{clean_text}'")
                    return clean_text
        except sr.UnknownValueError:
            pass
        except Exception as e:
            logger.debug(f"SpeechRecognition fallback error: {e}")

        return ""

import io
from typing import Optional
import numpy as np
import soundfile as sf
from openai import OpenAI
from app.config import settings
from app.utils.logger import logger

class WhisperSTT:
    """Speech-to-Text transcriber using OpenAI Whisper API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.client: Optional[OpenAI] = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initializes OpenAI API client for audio transcription."""
        if not settings.is_api_key_valid:
            logger.warning("OpenAI API key missing. Whisper STT disabled.")
            self.client = None
            return

        try:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("Whisper STT client successfully initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client for STT: {e}")
            self.client = None

    def transcribe(self, audio_data: np.ndarray, sample_rate: int = settings.SAMPLE_RATE) -> str:
        """Transcribes raw numpy float32 audio array into text using Whisper API.
        
        Args:
            audio_data: Float32 numpy audio waveform array.
            sample_rate: Sampling frequency in Hz.
            
        Returns:
            str: Transcribed text string.
        """
        if not self.client:
            self._initialize_client()
            if not self.client:
                logger.error("Cannot transcribe audio: OpenAI API client unavailable.")
                return ""

        if len(audio_data) == 0:
            return ""

        try:
            # Convert numpy audio array into WAV format in-memory BytesIO buffer
            byte_io = io.BytesIO()
            byte_io.name = "audio.wav"
            sf.write(byte_io, audio_data, sample_rate, format="WAV", subtype="PCM_16")
            byte_io.seek(0)

            logger.debug("Sending audio clip to OpenAI Whisper API...")
            response = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=byte_io,
                language="en"
            )

            transcribed_text = response.text.strip()
            logger.info(f"Whisper Transcription: '{transcribed_text}'")
            return transcribed_text

        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            return ""

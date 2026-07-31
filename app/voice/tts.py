import io
from typing import Optional, Tuple
import numpy as np
import soundfile as sf
from elevenlabs.client import ElevenLabs
import pyttsx3
from app.config import settings
from app.utils.logger import logger

class VoiceTTS:
    """Text-to-Speech synthesizer supporting ElevenLabs with pyttsx3 fallback."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        voice_id: Optional[str] = None
    ):
        self.api_key = api_key or settings.ELEVENLABS_API_KEY
        self.voice_id = voice_id or settings.ELEVENLABS_VOICE_ID
        self.elevenlabs_client: Optional[ElevenLabs] = None
        self._init_elevenlabs()

    def _init_elevenlabs(self) -> None:
        """Initializes ElevenLabs client if key is configured."""
        if settings.is_elevenlabs_key_valid:
            try:
                self.elevenlabs_client = ElevenLabs(api_key=self.api_key)
                logger.info(f"ElevenLabs TTS initialized with voice_id: {self.voice_id}")
            except Exception as e:
                logger.error(f"Failed to initialize ElevenLabs client: {e}")
                self.elevenlabs_client = None
        else:
            logger.info("ElevenLabs key not provided; will use local pyttsx3 fallback.")
            self.elevenlabs_client = None

    def synthesize(self, text: str) -> Tuple[Optional[np.ndarray], int]:
        """Synthesizes text into numpy float32 audio array and sample rate.
        
        Args:
            text: Text to synthesize.
            
        Returns:
            Tuple[Optional[np.ndarray], int]: Audio waveform array and sample rate.
        """
        trimmed = text.strip()
        if not trimmed:
            return None, settings.SAMPLE_RATE

        # Try ElevenLabs first if configured
        if self.elevenlabs_client:
            try:
                logger.debug(f"Synthesizing speech via ElevenLabs API for: '{trimmed[:30]}...'")
                audio_stream = self.elevenlabs_client.generate(
                    text=trimmed,
                    voice=self.voice_id,
                    model="eleven_multilingual_v2"
                )

                # Collect binary chunks into byte buffer
                audio_bytes = b"".join(audio_stream)
                byte_io = io.BytesIO(audio_bytes)
                audio_data, sr = sf.read(byte_io, dtype="float32")

                # If stereo, convert to mono
                if len(audio_data.shape) > 1 and audio_data.shape[1] > 1:
                    audio_data = np.mean(audio_data, axis=1)

                logger.info(f"Synthesized ElevenLabs voice output ({len(audio_data)} samples)")
                return audio_data, sr

            except Exception as e:
                logger.warning(f"ElevenLabs synthesis failed: {e}. Falling back to pyttsx3.")

        # Fallback to local pyttsx3 synthesis
        return self._synthesize_pyttsx3(trimmed)

    def _synthesize_pyttsx3(self, text: str) -> Tuple[Optional[np.ndarray], int]:
        """Local offline TTS synthesis fallback using pyttsx3."""
        try:
            engine = pyttsx3.init()
            # Select female voice if available
            voices = engine.getProperty("voices")
            for voice in voices:
                if "female" in voice.name.lower() or "zira" in voice.name.lower() or "eva" in voice.name.lower():
                    engine.setProperty("voice", voice.id)
                    break

            engine.setProperty("rate", 175)  # Natural speaking rate
            
            import tempfile, os
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_path = tmp_file.name

            engine.save_to_file(text, tmp_path)
            engine.runAndWait()

            audio_data, sr = sf.read(tmp_path, dtype="float32")
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

            if len(audio_data.shape) > 1 and audio_data.shape[1] > 1:
                audio_data = np.mean(audio_data, axis=1)

            logger.info(f"Synthesized pyttsx3 local voice output ({len(audio_data)} samples)")
            return audio_data, sr

        except Exception as e:
            logger.error(f"Local pyttsx3 TTS synthesis failed: {e}")
            return None, settings.SAMPLE_RATE

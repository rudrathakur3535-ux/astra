import threading
from typing import Optional, Union
import numpy as np
import sounddevice as sd
from app.config import settings
from app.utils.logger import logger

class SpeakerEngine:
    """Thread-safe, interruptible audio speaker playback engine."""

    def __init__(self, sample_rate: int = settings.SAMPLE_RATE):
        self.sample_rate = sample_rate
        self._is_playing = False
        self._interrupt_event = threading.Event()
        self._lock = threading.Lock()

    def play_audio(self, audio_data: np.ndarray, samplerate: Optional[int] = None) -> bool:
        """Plays numpy float/int audio array synchronously with support for interruption.
        
        Args:
            audio_data: Audio waveform numpy array.
            samplerate: Sample rate of audio (defaults to configured settings rate).
            
        Returns:
            bool: True if completed fully, False if interrupted.
        """
        rate = samplerate or self.sample_rate

        with self._lock:
            self._is_playing = True
            self._interrupt_event.clear()

        logger.debug(f"Starting audio playback ({len(audio_data)} samples at {rate}Hz)")

        try:
            # Play in non-blocking sounddevice stream while checking interrupt event
            stream = sd.OutputStream(samplerate=rate, channels=1, dtype="float32")
            stream.start()

            block_size = 1024
            for i in range(0, len(audio_data), block_size):
                if self._interrupt_event.is_set():
                    logger.info("Speaker playback interrupted by user.")
                    stream.stop()
                    stream.close()
                    with self._lock:
                        self._is_playing = False
                    return False

                chunk = audio_data[i:i + block_size]
                stream.write(chunk)

            stream.stop()
            stream.close()

        except Exception as e:
            logger.error(f"Error during audio playback: {e}")

        with self._lock:
            self._is_playing = False

        return True

    def interrupt(self) -> None:
        """Signals active audio playback to halt immediately."""
        self._interrupt_event.set()
        logger.debug("Speaker interrupt signal dispatched.")

    def is_playing(self) -> bool:
        """Returns True if audio is currently playing."""
        with self._lock:
            return self._is_playing

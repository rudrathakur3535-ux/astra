import time
from typing import Optional, List
import numpy as np
from app.voice.microphone import MicrophoneRecorder
from app.utils.logger import logger

class VoiceListener:
    """Voice activity detection and audio phrase collector."""

    def __init__(
        self,
        recorder: MicrophoneRecorder,
        energy_threshold: float = 0.015,
        silence_duration: float = 1.2,
        min_speech_duration: float = 0.5,
        max_speech_duration: float = 15.0
    ):
        self.recorder = recorder
        self.energy_threshold = energy_threshold
        self.silence_duration = silence_duration
        self.min_speech_duration = min_speech_duration
        self.max_speech_duration = max_speech_duration

    def calculate_rms(self, audio_chunk: np.ndarray) -> float:
        """Calculates Root Mean Square (RMS) energy of an audio frame."""
        if len(audio_chunk) == 0:
            return 0.0
        return float(np.sqrt(np.mean(np.square(audio_chunk))))

    def listen_for_phrase(self, stop_checker: Optional[callable] = None) -> Optional[np.ndarray]:
        """Collects microphone audio frames until user finishes speaking.
        
        Args:
            stop_checker: Optional callback returning True if listening should cancel.
            
        Returns:
            np.ndarray of concatenated audio frames, or None if cancelled/no speech.
        """
        speech_buffer: List[np.ndarray] = []
        is_speaking = False
        last_speech_time = time.time()
        start_time = time.time()

        logger.debug("Listening for voice input...")

        while True:
            if stop_checker and stop_checker():
                return None

            chunk = self.recorder.get_chunk(block=True, timeout=0.1)
            if chunk is None:
                continue

            rms = self.calculate_rms(chunk)

            if rms > self.energy_threshold:
                if not is_speaking:
                    is_speaking = True
                    logger.debug(f"Speech detected (RMS: {rms:.4f})")
                is_speaking = True
                last_speech_time = time.time()
                speech_buffer.append(chunk)

            elif is_speaking:
                # Still within silence duration after speaking started
                speech_buffer.append(chunk)
                silence_elapsed = time.time() - last_speech_time

                if silence_elapsed >= self.silence_duration:
                    logger.debug("Silence detected, completing phrase collection.")
                    break

            # Prevent infinite recording loop exceeding max duration
            if is_speaking and (time.time() - start_time) > self.max_speech_duration:
                logger.warning("Max speech duration reached. Finalizing recording.")
                break

        if not speech_buffer:
            return None

        audio_clip = np.concatenate(speech_buffer)
        duration = len(audio_clip) / self.recorder.sample_rate

        if duration < self.min_speech_duration:
            logger.debug(f"Audio duration ({duration:.2f}s) below minimum speech threshold.")
            return None

        logger.info(f"Captured audio phrase ({duration:.2f} seconds)")
        return MicrophoneRecorder.normalize_audio(audio_clip)

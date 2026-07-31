import queue
import threading
from typing import Optional
import numpy as np
import sounddevice as sd
from app.config import settings
from app.utils.logger import logger

class MicrophoneRecorder:
    """Thread-safe microphone capture manager using sounddevice InputStream."""

    def __init__(
        self,
        sample_rate: int = settings.SAMPLE_RATE,
        channels: int = settings.AUDIO_CHANNELS,
        block_size: int = 1024
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.block_size = block_size
        self.audio_queue: queue.Queue[np.ndarray] = queue.Queue()
        self.stream: Optional[sd.InputStream] = None
        self._is_recording = False
        self._lock = threading.Lock()

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info: dict, status: sd.CallbackFlags) -> None:
        """Internal callback invoked by sounddevice stream for every audio chunk."""
        if status:
            logger.warning(f"Sounddevice callback status warning: {status}")
        if self._is_recording:
            # Flatten audio chunk and copy to avoid buffer overwrites
            chunk = indata.copy().flatten()
            self.audio_queue.put(chunk)

    def start(self) -> None:
        """Starts continuous microphone recording stream."""
        with self._lock:
            if self._is_recording:
                return

            self.clear_queue()
            try:
                self.stream = sd.InputStream(
                    samplerate=self.sample_rate,
                    channels=self.channels,
                    blocksize=self.block_size,
                    dtype="float32",
                    callback=self._audio_callback
                )
                self.stream.start()
                self._is_recording = True
                logger.info(f"Microphone recording started (Sample Rate: {self.sample_rate}Hz)")
            except Exception as e:
                logger.error(f"Failed to start microphone stream: {e}")
                self._is_recording = False

    def stop(self) -> None:
        """Stops microphone recording stream."""
        with self._lock:
            if not self._is_recording:
                return
            self._is_recording = False
            if self.stream:
                try:
                    self.stream.stop()
                    self.stream.close()
                except Exception as e:
                    logger.error(f"Error stopping microphone stream: {e}")
                self.stream = None
            logger.info("Microphone recording stopped.")

    def is_recording(self) -> bool:
        """Returns recording status."""
        return self._is_recording

    def get_chunk(self, block: bool = True, timeout: Optional[float] = None) -> Optional[np.ndarray]:
        """Gets next audio chunk from queue."""
        try:
            return self.audio_queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None

    def clear_queue(self) -> None:
        """Empties the pending audio queue."""
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

    @staticmethod
    def normalize_audio(audio_data: np.ndarray) -> np.ndarray:
        """Normalizes audio volume float values to [-1.0, 1.0]."""
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            return audio_data / max_val
        return audio_data

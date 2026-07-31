import asyncio
import threading
from enum import Enum, auto
from typing import Optional, Callable, Dict, Any
import numpy as np

from app.voice.microphone import MicrophoneRecorder
from app.voice.listener import VoiceListener
from app.voice.speaker import SpeakerEngine
from app.voice.stt import WhisperSTT
from app.voice.tts import VoiceTTS
from app.voice.wakeword import WakeWordDetector
from app.config import settings
from app.utils.logger import logger

class VoiceState(Enum):
    OFFLINE = auto()
    LISTENING_FOR_WAKEWORD = auto()
    RECORDING_USER_PROMPT = auto()
    PROCESSING_THOUGHTS = auto()
    SPEAKING_RESPONSE = auto()

class AudioManager:
    """Central manager orchestrating microphone input, STT, wake word, TTS, and speaker playback."""

    def __init__(
        self,
        on_state_change: Optional[Callable[[VoiceState], None]] = None,
        on_transcript: Optional[Callable[[str, str], None]] = None
    ):
        self.on_state_change = on_state_change
        self.on_transcript = on_transcript

        self.state = VoiceState.OFFLINE
        self.recorder = MicrophoneRecorder()
        self.listener = VoiceListener(self.recorder)
        self.speaker = SpeakerEngine()
        self.stt = WhisperSTT()
        self.tts = VoiceTTS()
        self.wake_detector = WakeWordDetector()

        self._running = False
        self._voice_loop_thread: Optional[threading.Thread] = None
        self._chat_processor_callback: Optional[Callable[[str], str]] = None

    def set_chat_processor(self, callback: Callable[[str], str]) -> None:
        """Sets the LLM Brain chat processor function to handle user prompts."""
        self._chat_processor_callback = callback

    def _set_state(self, new_state: VoiceState) -> None:
        """Updates internal state and triggers UI notification callback."""
        self.state = new_state
        logger.debug(f"Voice state updated: {new_state.name}")
        if self.on_state_change:
            try:
                self.on_state_change(new_state)
            except Exception as e:
                logger.error(f"Error in on_state_change callback: {e}")

    def start(self) -> None:
        """Starts background voice management thread."""
        if self._running:
            return

        self._running = True
        self.recorder.start()
        self._voice_loop_thread = threading.Thread(target=self._run_voice_loop, daemon=True)
        self._voice_loop_thread.start()
        logger.info("Voice Subsystem AudioManager started.")

    def stop(self) -> None:
        """Stops background voice management thread and shuts down hardware streams."""
        if not self._running:
            return

        self._running = False
        self.speaker.interrupt()
        self.recorder.stop()
        self._set_state(VoiceState.OFFLINE)
        logger.info("Voice Subsystem AudioManager stopped.")

    def interrupt_speech(self) -> None:
        """Interrupts Astra if she is currently speaking."""
        if self.speaker.is_playing():
            logger.info("User requested speech interruption.")
            self.speaker.interrupt()

    def _run_voice_loop(self) -> None:
        """Continuous background loop monitoring mic audio, wake words, and prompt responses."""
        self._set_state(VoiceState.LISTENING_FOR_WAKEWORD)

        while self._running:
            try:
                # 1. Continuous audio phrase listening
                audio_clip = self.listener.listen_for_phrase(stop_checker=lambda: not self._running)
                if audio_clip is None or len(audio_clip) == 0:
                    continue

                # 2. Transcribe audio phrase using Whisper STT
                transcript = self.stt.transcribe(audio_clip)
                if not transcript.strip():
                    continue

                logger.info(f"Heard audio transcript: '{transcript}'")

                # If Astra is currently speaking and user says "stop" or interrupts
                if self.speaker.is_playing() and "stop" in transcript.lower():
                    self.interrupt_speech()
                    continue

                # 3. Process Wake Word or Active Conversation State
                if self.state == VoiceState.LISTENING_FOR_WAKEWORD:
                    is_wake, user_prompt = self.wake_detector.check_wake_word(transcript)
                    if not is_wake:
                        continue

                    # Wake word matched! Notify UI transcript
                    if self.on_transcript:
                        self.on_transcript("user", f"[Wake Word Detected]: {transcript}")

                    # If prompt followed wake word immediately (e.g. "Hey Astra, what is Binary Search?")
                    if user_prompt:
                        self._process_and_speak(user_prompt)
                    else:
                        # Greet user and transition to active recording state
                        self._speak_text(f"Yes {settings.USER_NAME}?")
                        self._set_state(VoiceState.RECORDING_USER_PROMPT)

                elif self.state == VoiceState.RECORDING_USER_PROMPT:
                    # Directly process user prompt
                    self._process_and_speak(transcript)
                    # Return back to listening for wake word
                    self._set_state(VoiceState.LISTENING_FOR_WAKEWORD)

            except Exception as e:
                logger.error(f"Error in main voice processing loop: {e}", exc_info=True)
                self._set_state(VoiceState.LISTENING_FOR_WAKEWORD)

    def _process_and_speak(self, prompt: str) -> None:
        """Routes user prompt to LLM brain callback and speaks the generated reply."""
        if not prompt.strip():
            return

        self._set_state(VoiceState.PROCESSING_THOUGHTS)

        if self.on_transcript:
            self.on_transcript("user", prompt)

        # Obtain response from LLM brain if callback registered
        response_text = ""
        if self._chat_processor_callback:
            try:
                response_text = self._chat_processor_callback(prompt)
            except Exception as e:
                logger.error(f"Error getting LLM response for voice: {e}")
                response_text = "I experienced an error processing your request."
        else:
            response_text = f"Hello {settings.USER_NAME}, voice mode is active and listening!"

        if response_text and self.on_transcript:
            self.on_transcript("assistant", response_text)

        # Speak output response
        self._speak_text(response_text)

    def _speak_text(self, text: str) -> None:
        """Synthesizes text and plays audio output through speaker engine."""
        self._set_state(VoiceState.SPEAKING_RESPONSE)
        audio_data, samplerate = self.tts.synthesize(text)
        if audio_data is not None and len(audio_data) > 0:
            self.speaker.play_audio(audio_data, samplerate=samplerate)
        self._set_state(VoiceState.LISTENING_FOR_WAKEWORD)

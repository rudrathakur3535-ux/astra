"""
Voice Subsystem Module - Audio capture, VAD, STT (Whisper), TTS (ElevenLabs), Wake Word, and AudioManager.
"""

from app.voice.microphone import MicrophoneRecorder
from app.voice.listener import VoiceListener
from app.voice.speaker import SpeakerEngine
from app.voice.stt import WhisperSTT
from app.voice.tts import VoiceTTS
from app.voice.wakeword import WakeWordDetector
from app.voice.audio_manager import AudioManager, VoiceState

__all__ = [
    "MicrophoneRecorder",
    "VoiceListener",
    "SpeakerEngine",
    "WhisperSTT",
    "VoiceTTS",
    "WakeWordDetector",
    "AudioManager",
    "VoiceState"
]

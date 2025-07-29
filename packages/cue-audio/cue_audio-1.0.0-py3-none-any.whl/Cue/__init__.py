"""
Cue - Simple, elegant spatial audio orchestration

Build simply, work effortlessly, fail gracefully.
"""

from .controller import AudioController
from .clip import AudioClip
from .exceptions import AudioError, DeviceError, MQTTError, ClipError, PolyphonyError, ConnectionError

__version__ = "1.0.0"
__author__ = "Cue Audio Library"
__description__ = "MQTT-controlled spatial audio system for immersive experiences"

__all__ = [
    "AudioController", 
    "AudioClip", 
    "AudioError", 
    "DeviceError", 
    "MQTTError",
    "ClipError",
    "PolyphonyError", 
    "ConnectionError"
] 
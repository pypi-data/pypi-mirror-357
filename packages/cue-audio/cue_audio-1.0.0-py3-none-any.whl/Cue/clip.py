"""
Cue AudioClip - Declarative audio clip configuration
"""

import os
import wave
from dataclasses import dataclass
from typing import Dict, Optional
from .exceptions import ClipError

@dataclass
class AudioClip:
    """
    Declarative audio clip configuration
    
    Example:
        clip = AudioClip(
            file="thunder.wav",
            volume=1.0,
            loop=True,
            mqtt_triggers={"storm/lightning": "play"}
        )
    """
    file: str
    volume: float = 1.0
    fade_out: float = 0.0
    fade_in: float = 0.0
    length: Optional[float] = None
    choke_group: Optional[str] = None
    mqtt_triggers: Optional[Dict[str, str]] = None
    loop: bool = False
    auto_play: bool = False
    routing: Optional[Dict[str, str]] = None  # Maps channels to speakers (e.g. {'right': 'left'})
    poly: bool = False  # Allow multiple instances to play simultaneously
    max_poly: int = 4   # Maximum number of simultaneous instances (when poly=True)
    retrigger: bool = True  # Allow retriggering while sound is playing
    
    def __post_init__(self):
        """Validate clip configuration after creation"""
        if self.volume < 0 or self.volume > 2:
            raise ClipError(f"Volume must be between 0 and 2, got {self.volume}")
        
        if self.fade_in < 0 or self.fade_out < 0:
            raise ClipError("Fade times must be positive")
            
        if self.mqtt_triggers:
            valid_actions = {"play", "stop"}
            for topic, action in self.mqtt_triggers.items():
                if action not in valid_actions:
                    raise ClipError(f"Invalid MQTT action '{action}'. Must be one of: {valid_actions}")
    
    def validate_file(self) -> bool:
        """
        Validate that the audio file exists and is readable
        Returns True if valid, raises ClipError if not
        """
        if not os.path.exists(self.file):
            raise ClipError(f"Audio file not found: {self.file}")
        
        try:
            with wave.open(self.file, 'rb') as wf:
                if wf.getnchannels() != 2:
                    raise ClipError(f"Expected stereo file, got {wf.getnchannels()} channels: {self.file}")
                
                if wf.getsampwidth() not in [2, 3, 4]:  # 16, 24, 32 bit
                    raise ClipError(f"Unsupported bit depth in file: {self.file}")
                    
        except wave.Error as e:
            raise ClipError(f"Invalid WAV file {self.file}: {e}")
        
        return True
    
    @property
    def file_path(self) -> str:
        """Alias for compatibility with existing code"""
        return self.file 
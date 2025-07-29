"""
Cue Exceptions - Fail gracefully with helpful error messages
"""

class AudioError(Exception):
    """Base exception for audio-related errors"""
    pass

class DeviceError(AudioError):
    """Audio device configuration or access errors"""
    pass

class MQTTError(AudioError):
    """MQTT connection or communication errors"""
    pass

class ClipError(AudioError):
    """Audio clip loading or processing errors"""
    pass

class PolyphonyError(AudioError):
    """Polyphonic audio limits exceeded"""
    pass

class ConnectionError(AudioError):
    """Network or connection-related errors"""
    pass 
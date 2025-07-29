"""
Cue AudioController - The heart of the spatial audio system

Build simply, work effortlessly, fail gracefully.
"""

import pyaudio
import paho.mqtt.client as mqtt
import wave
import numpy as np
import json
import time
import threading
from typing import Dict, Optional, Tuple
from .clip import AudioClip
from .exceptions import AudioError, DeviceError, MQTTError, ClipError

class AudioController:
    """
    Simple, elegant spatial audio orchestration
    
    Example:
        audio = AudioController(channels="stereo")
        audio.register_clip("thunder", AudioClip(file="thunder.wav"))
        audio.start()
    """
    
    def __init__(self, 
                 channels: str = "stereo",
                 device: str = "default", 
                 mqtt_broker: Optional[str] = None,
                 mqtt_credentials: Optional[Tuple[str, str]] = None,
                 mqtt_port: int = 1883):
        """
        Initialize Cue audio controller
        
        Args:
            channels: "stereo" or "5.1"
            device: "default", specific device name, or None for auto-detect
            mqtt_broker: MQTT broker IP/hostname, None to disable MQTT
            mqtt_credentials: (username, password) tuple, None for no auth
            mqtt_port: MQTT broker port (default 1883)
        """
        # Build simply - validate and set sensible defaults
        self.channels_config = self._validate_channels(channels)
        self.device_config = device
        self.mqtt_config = (mqtt_broker, mqtt_credentials, mqtt_port) if mqtt_broker else None
        
        # Initialize data structures BEFORE starting audio stream
        self.clips: Dict[str, AudioClip] = {}
        self.active_sounds: Dict[str, dict] = {}
        self.mqtt_bindings: Dict[str, list] = {}
        self.choke_groups: Dict[str, list] = {}
        
        # Thread safety for audio loading
        self._audio_lock = threading.Lock()
        self._last_play_time: Dict[str, float] = {}  # Debounce rapid messages
        
        # Audio system components (initialized in start())
        self.pa: Optional[pyaudio.PyAudio] = None
        self.stream: Optional[pyaudio.Stream] = None
        self.mqtt_client: Optional[mqtt.Client] = None
        
        # Configure channel layout
        if channels == "stereo":
            self.channels = 2
            self.channel_indices = {"left": 0, "right": 1}
        elif channels == "5.1":
            self.channels = 6
            self.channel_indices = {
                "front_left": 0, "front_right": 1, "center": 2,
                "subwoofer": 3, "rear_left": 4, "rear_right": 5
            }
        
        self.is_surround = channels == "5.1"
        self.mix_buffer = None
        self._running = False
    
    def register_clip(self, name: str, clip: AudioClip) -> None:
        """
        Register an audio clip - fails gracefully if file missing
        
        Args:
            name: Unique identifier for this clip
            clip: AudioClip configuration
        """
        try:
            # Validate clip configuration and file
            clip.validate_file()
            self.clips[name] = clip
            print(f"✅ Registered clip: {name}")
            
            # Register MQTT triggers if clip has them
            if clip.mqtt_triggers and self.mqtt_config:
                for topic, action in clip.mqtt_triggers.items():
                    if topic not in self.mqtt_bindings:
                        self.mqtt_bindings[topic] = []
                    self.mqtt_bindings[topic].append((name, action))
                    
        except ClipError as e:
            print(f"⚠️  Warning: Could not register clip '{name}': {e}")
            # Continue anyway - maybe file will appear later
    
    def start(self) -> None:
        """
        Start the audio system - fail gracefully with helpful errors
        """
        try:
            print("🎵 Starting Cue audio system...")
            
            # Setup audio system
            self._setup_audio()
            
            # Setup MQTT if configured
            if self.mqtt_config:
                try:
                    self._setup_mqtt()
                    print("📡 MQTT connected")
                except MQTTError as e:
                    print(f"⚠️  MQTT disabled: {e}")
                    # Continue without MQTT
            
            # Start auto-play clips
            self._start_auto_clips()
            
            self._running = True
            print("🎵 Cue audio system running...")
            
            # Run forever (blocking)
            self._run_forever()
            
        except DeviceError as e:
            raise AudioError(f"Audio device problem: {e}")
        except Exception as e:
            raise AudioError(f"Failed to start audio system: {e}")
    
    def stop(self) -> None:
        """Stop the audio system gracefully"""
        print("👋 Stopping Cue audio system...")
        self._running = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.pa:
            self.pa.terminate()
            
        if self.mqtt_client:
            self.mqtt_client.disconnect()
    
    def _validate_channels(self, channels: str) -> str:
        """Validate channel configuration"""
        if channels not in ["stereo", "5.1"]:
            raise ValueError("channels must be 'stereo' or '5.1'")
        return channels
    
    def _setup_audio(self) -> None:
        """Setup PyAudio system with device detection"""
        try:
            self.pa = pyaudio.PyAudio()
            device_index = self._find_audio_device()
            
            # Initialize mix buffer
            self.mix_buffer = np.zeros((1024, self.channels), dtype=np.float32)
            
            # Open audio stream
            self.stream = self.pa.open(
                format=pyaudio.paFloat32,
                channels=self.channels,
                rate=44100,
                output=True,
                frames_per_buffer=1024,
                output_device_index=device_index,
                stream_callback=self._audio_callback
            )
            self.stream.start_stream()
            
            device_info = self.pa.get_device_info_by_index(device_index)
            print(f"🔊 Audio: {self.channels_config} on '{device_info['name']}'")
            
        except Exception as e:
            raise DeviceError(f"Could not setup audio device: {e}")
    
    def _find_audio_device(self) -> int:
        """Find suitable audio device, preferring default"""
        print("🔍 Detecting audio devices...")
        
        default_device = None
        suitable_device = None
        
        # Get default device
        try:
            default_info = self.pa.get_default_output_device_info()
            default_device = default_info['index']
        except:
            pass
        
        # Check all devices
        for i in range(self.pa.get_device_count()):
            info = self.pa.get_device_info_by_index(i)
            
            if default_device is not None and info['index'] == default_device:
                print(f"🎯 Default device: {info['name']} ({info['maxOutputChannels']} channels)")
                if info['maxOutputChannels'] >= self.channels:
                    print(f"🎯 Default device supports {self.channels} channels - using this!")
                    return default_device
            
            if info['maxOutputChannels'] >= self.channels and suitable_device is None:
                suitable_device = i
                print(f"🎯 Suitable for {self.channels} channels: {info['name']}")
        
        if suitable_device is not None:
            info = self.pa.get_device_info_by_index(suitable_device)
            print(f"🎯 Using suitable device: {info['name']}")
            return suitable_device
            
        raise DeviceError(f"No audio device found supporting {self.channels} channels")
    
    def _setup_mqtt(self) -> None:
        """Setup MQTT client with authentication"""
        if not self.mqtt_config:
            return
            
        broker, credentials, port = self.mqtt_config
        
        try:
            # Keep it simple like the original working version
            self.mqtt_client = mqtt.Client()
            
            if credentials:
                username, password = credentials
                self.mqtt_client.username_pw_set(username, password)
            
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_message = self._on_mqtt_message
            
            self.mqtt_client.connect(broker, port, 60)
            # Don't start background thread here - do it in run_forever
            
        except Exception as e:
            raise MQTTError(f"Could not connect to MQTT broker {broker}: {e}")
    
    def _on_mqtt_connect(self, client, userdata, flags, reason_code, properties=None):
        """Handle MQTT connection"""
        print(f"📡 MQTT connected (code: {reason_code})")
        
        # Subscribe to all registered topics
        for topic in self.mqtt_bindings.keys():
            client.subscribe(topic)
            print(f"📡 Subscribed to: {topic}")
    
    def _on_mqtt_disconnect(self, client, userdata, rc):
        """Handle MQTT disconnection"""
        if rc != 0:
            print(f"⚠️  MQTT disconnected unexpectedly (code: {rc})")
        else:
            print("📡 MQTT disconnected gracefully")
    
    def _on_mqtt_log(self, client, userdata, level, buf):
        """Handle MQTT logging - only show errors"""
        if level == mqtt.MQTT_LOG_ERR:
            print(f"❌ MQTT Error: {buf}")
    
    def _on_mqtt_message(self, client, userdata, msg):
        """Handle incoming MQTT messages with error protection"""
        try:
            topic = msg.topic
            print(f"📡 MQTT: {topic}")
            
            # Validate message structure
            if not hasattr(msg, 'payload') or msg.payload is None:
                print(f"⚠️  Invalid MQTT message structure on {topic}")
                return
            
            # Check for registered clip triggers
            if topic in self.mqtt_bindings:
                for clip_name, action in self.mqtt_bindings[topic]:
                    if action == "play":
                        self._handle_play(clip_name, {})
                    elif action == "stop":
                        self._handle_stop(clip_name)
                return
            
            # Try JSON parsing for other messages
            try:
                payload = json.loads(msg.payload.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                try:
                    payload = {"value": msg.payload.decode('utf-8', errors='ignore')}
                except Exception:
                    payload = {"value": str(msg.payload)}
            
            topic_parts = msg.topic.split('/')
            
            if len(topic_parts) < 2:
                return
                
            command = topic_parts[1]
            target = topic_parts[2] if len(topic_parts) > 2 else None
            
            if command == "play" and target:
                self._handle_play(target, payload)
            elif command == "stop" and target:
                self._handle_stop(target)
                        
        except Exception as e:
            print(f"❌ MQTT message error: {e}")
            # Don't re-raise - keep MQTT running
    
    def _start_auto_clips(self) -> None:
        """Start clips marked for auto-play"""
        for name, clip in self.clips.items():
            if clip.auto_play:
                print(f"🎵 Auto-playing: {name}")
                self._handle_play(name, {})
    
    def _run_forever(self) -> None:
        """Main event loop - keep audio running even if MQTT fails"""
        try:
            if self.mqtt_client:
                # Keep trying MQTT with reconnection
                while self._running:
                    try:
                        print("📡 MQTT loop starting...")
                        self.mqtt_client.loop_forever()
                        # If we get here, loop_forever exited (shouldn't happen)
                        break
                    except Exception as e:
                        print(f"⚠️  MQTT failed: {e}")
                        print("🎵 Audio continues running, attempting MQTT reconnect in 5s...")
                        time.sleep(5)
                        try:
                            self.mqtt_client.reconnect()
                            print("📡 MQTT reconnected!")
                        except Exception as reconnect_error:
                            print(f"❌ MQTT reconnect failed: {reconnect_error}")
                            # Keep trying...
            else:
                # No MQTT, just keep audio running
                print("🎵 Audio-only mode (no MQTT)")
                while self._running:
                    time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
            pass
    
    # Real Audio Processing (ported from original)
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback for continuous audio output"""
        self.mix_buffer.fill(0)
        
        for sound_id, sound_data in list(self.active_sounds.items()):
            if not sound_data['active']:
                continue
                
            clip = sound_data['clip']
            position = sound_data['position']
            data = sound_data['data']
            start_time = sound_data['start_time']
            current_time = time.time()
            
            # Calculate current volume based on fade in/out
            current_volume = clip.volume
            if clip.fade_in > 0:
                fade_in_progress = min(1.0, (current_time - start_time) / clip.fade_in)
                current_volume *= fade_in_progress
            
            if sound_data.get('stopping') and clip.fade_out > 0:
                # Use the original stop_time that was set when the fade out began
                stop_time = sound_data['stop_time']
                fade_out_progress = 1.0 - min(1.0, (current_time - stop_time) / clip.fade_out)
                current_volume *= fade_out_progress
                if fade_out_progress <= 0:
                    sound_data['active'] = False
                    continue
            
            # Get chunk of stereo audio data
            chunk_end = position + frame_count
            if chunk_end > len(data):
                if clip.loop:
                    chunk = np.concatenate([
                        data[position:],
                        data[:chunk_end - len(data)]
                    ])
                    sound_data['position'] = chunk_end - len(data)
                else:
                    chunk = data[position:]
                    sound_data['active'] = False
            else:
                chunk = data[position:chunk_end]
                sound_data['position'] = chunk_end
            
            # Route stereo channels to speakers with current_volume
            if clip.routing:
                for channel, speaker in clip.routing.items():
                    if speaker in self.channel_indices:
                        chan_idx = self.channel_indices[speaker]
                        chan_data = chunk[:, 0 if channel == "left" else 1]
                        self.mix_buffer[:len(chan_data), chan_idx] += chan_data * current_volume
            else:
                # Default routing: stereo to left/right
                self.mix_buffer[:len(chunk), 0] += chunk[:, 0] * current_volume
                if self.channels > 1:
                    self.mix_buffer[:len(chunk), 1] += chunk[:, 1] * current_volume
        
        # Apply soft limiting to prevent harsh distortion
        threshold = 0.95  # Start limiting at 95% of full scale
        ratio = 0.7      # Gentle compression ratio
        knee = 0.1       # Soft knee width
        
        # Calculate gain reduction
        peak = np.max(np.abs(self.mix_buffer))
        if peak > threshold:
            # Soft knee compression
            if peak < threshold + knee:
                # In the knee region
                db_reduction = ((peak - threshold) / knee) * ((peak - threshold) / 2)
            else:
                # Above knee
                db_reduction = (peak - threshold) + ((peak - threshold - knee) * (ratio - 1))
            
            # Convert to linear gain
            gain_reduction = 10 ** (-db_reduction / 20)
            
            # Apply gain reduction
            self.mix_buffer *= gain_reduction
        
        # Final hard clip as safety
        np.clip(self.mix_buffer, -1, 1, out=self.mix_buffer)
        return (self.mix_buffer.tobytes(), pyaudio.paContinue)
    
    def _handle_play(self, clip_name: str, payload: dict):
        """Handle play command for a clip"""
        if clip_name not in self.clips:
            print(f"⚠️  Unknown clip: {clip_name}")
            return
        
        # Thread safety and debouncing
        with self._audio_lock:
            current_time = time.time()
            clip = self.clips[clip_name]
            
            # Check retrigger setting ONLY for play commands
            if not clip.retrigger and payload.get('action', 'play') == 'play':
                # For polyphonic clips, check if any instance is playing
                if clip.poly:
                    poly_instances = [k for k in self.active_sounds.keys() if k.startswith(f"{clip_name}_poly_")]
                    if any(self.active_sounds[k]['active'] for k in poly_instances):
                        print(f"⏸️  Skipping retrigger of polyphonic clip: {clip_name}")
                        return
                # For non-polyphonic clips, check if the main instance is playing
                elif clip_name in self.active_sounds:
                    sound_data = self.active_sounds[clip_name]
                    # Only skip if actively playing (not fading out)
                    if sound_data['active'] and not sound_data.get('stopping'):
                        print(f"⏸️  Skipping retrigger of clip: {clip_name}")
                        return
                    # If it's fading out, let it continue fading
                    elif sound_data.get('stopping'):
                        print(f"⏸️  Clip is already fading out: {clip_name}")
                        return
            
            # Handle poly vs mono clips differently
            if clip.poly:
                # Polyphonic: allow multiple instances, with limit
                poly_instances = [k for k in self.active_sounds.keys() if k.startswith(f"{clip_name}_poly_")]
                
                if len(poly_instances) >= clip.max_poly:
                    # Remove oldest instance to make room
                    oldest_key = min(poly_instances, key=lambda k: self.active_sounds[k]['start_time'])
                    print(f"🔄 Poly limit reached, removing oldest: {oldest_key}")
                    del self.active_sounds[oldest_key]
                
                # Create new poly instance
                instance_id = f"{clip_name}_poly_{int(current_time * 1000) % 10000}"  # timestamp-based ID
                print(f"🎵 Playing poly: {instance_id}")
            else:
                # Monophonic: use clip name as instance ID
                instance_id = clip_name
                print(f"🎵 Playing: {instance_id}")
                
                # Stop any sounds in the same choke group BEFORE loading new sound
                if clip.choke_group:
                    print(f"🔇 Stopping other sounds in choke group: {clip.choke_group}")
                    if clip.choke_group in self.choke_groups:
                        for sound_id in list(self.choke_groups[clip.choke_group]):
                            if sound_id != clip_name:  # Don't stop ourselves
                                self._handle_stop_unsafe(sound_id)  # Use unsafe version since we have the lock
                        self.choke_groups[clip.choke_group] = []
                    else:
                        self.choke_groups[clip.choke_group] = []
                    self.choke_groups[clip.choke_group].append(clip_name)
            
            try:
                # Load wave file
                with wave.open(clip.file, 'rb') as wf:
                    channels = wf.getnchannels()
                    if channels != 2:
                        print(f"⚠️  Warning: Expected stereo file, got {channels} channels")
                        return
                        
                    sampwidth = wf.getsampwidth()
                    
                    # Read the entire file into memory
                    raw_data = wf.readframes(wf.getnframes())
                    
                    # Convert to float32 and normalize
                    if sampwidth == 2:  # 16-bit
                        data = np.frombuffer(raw_data, dtype=np.int16)
                        data = data.astype(np.float32) / 32768.0
                    else:
                        print(f"⚠️  Unsupported sample width: {sampwidth}")
                        return
                    
                    # Reshape to stereo
                    data = data.reshape(-1, 2)
                    print(f"📊 Loaded audio: {len(data)} samples")
                
                # Store sound data
                self.active_sounds[instance_id] = {
                    'data': data,
                    'position': 0,
                    'active': True,
                    'clip': clip,
                    'start_time': time.time()
                }
                
            except Exception as e:
                print(f"❌ Error loading audio file {clip.file}: {e}")

    def _handle_stop(self, clip_name: str):
        """Handle stop command for a clip (thread-safe)"""
        with self._audio_lock:
            self._handle_stop_unsafe(clip_name)
    
    def _handle_stop_unsafe(self, clip_name: str):
        """Handle stop command for a clip (unsafe - must be called with lock held)"""
        # Handle both mono and poly clips
        keys_to_stop = []
        
        # Find all instances of this clip (mono or poly)
        for key in self.active_sounds.keys():
            if key == clip_name or key.startswith(f"{clip_name}_poly_"):
                keys_to_stop.append(key)
        
        for key in keys_to_stop:
            if key in self.active_sounds:
                sound_data = self.active_sounds[key]
                clip = sound_data['clip']
                
                # Remove from choke group if present (only for base clip name)
                if key == clip_name and clip.choke_group and clip.choke_group in self.choke_groups:
                    if clip_name in self.choke_groups[clip.choke_group]:
                        self.choke_groups[clip.choke_group].remove(clip_name)
                
                # Only start a new fade out if we're not already fading out
                if not sound_data.get('stopping'):
                    if clip.fade_out > 0:
                        # Mark for fade out instead of immediate stop
                        sound_data['stopping'] = True
                        sound_data['stop_time'] = time.time()
                        print(f"⏹️  Fading out: {key} ({clip.fade_out}s)")
                    else:
                        sound_data['active'] = False
                        print(f"⏹️  Stopping: {key}")
                else:
                    print(f"⏹️  Already fading out: {key}")
    
    def _stop_choke_group(self, group: str, except_clip: str = None):
        """Stop all clips in a choke group except the specified one"""
        for clip_name, clip in self.clips.items():
            if clip.choke_group == group and clip_name != except_clip:
                self._handle_stop(clip_name) 
# Cue Enhancement Proposal

Practical audio control features to enhance immersive experiences.

## Proposed Features

### 1. Pan Control

Simple stereo positioning without full 5.1 complexity.

```python
AudioClip(
    file="footsteps.wav",
    pan=-0.3,  # Slightly left of center
    mqtt_triggers={"player/left": "play"}
)
```

**Implementation:**
- `pan` (float): Stereo pan position
- Range: `-1.0` (full left) to `1.0` (full right)
- Default: `0.0` (center)
- Applied during audio mixing using simple amplitude scaling

**Use Cases:**
- Positional footsteps in corridors
- Directional dialogue from NPCs
- Environmental effects (wind from windows)


### 2. Delay/Offset

Timing control for sequential audio events.

```python
AudioClip(
    file="thunder.wav",
    delay=2.5,  # 2.5 seconds after trigger
    mqtt_triggers={"storm/lightning": "play"}
)
```

**Implementation:**
- `delay` (float): Seconds to wait before starting playback
- Default: `0.0` (immediate)
- Uses threading timer for precise timing
- Delay applies to initial trigger only, not loops

**Use Cases:**
- Thunder following lightning
- Timed sequences (door creak, then footsteps)
- Staggered ambient layers


### 3. Random Volume Variation

Natural variation for repeated sounds.

```python
AudioClip(
    file="drip.wav",
    volume=0.6,
    random_volume=0.2,  # ±20% variation (0.48-0.72)
    loop=True
)
```

**Implementation:**
- `random_volume` (float): Variation as percentage of base volume
- Range: `0.0` to `1.0`
- Default: `0.0` (no variation)
- Applied per playback instance using `random.uniform()`

**Use Cases:**
- Water drips with natural variation
- Footsteps that don't sound mechanical
- Wind intensity fluctuation


### 4. Random Pitch Variation

Pitch variation for organic sound repetition.

```python
AudioClip(
    file="step.wav",
    random_pitch=2.0,  # ±2 semitones variation
    poly=True,
    mqtt_triggers={"player/walk": "play"}
)
```

**Implementation:**
- `random_pitch` (float): Variation in semitones
- Range: `0.0` to `12.0` (practical limit)
- Default: `0.0` (no variation)
- Applied via playback rate adjustment (2^(semitones/12))

**Use Cases:**
- Footsteps on different surfaces
- Multiple instances of same voice line
- Mechanical sounds with slight variation


## API Integration

These features integrate seamlessly with existing AudioClip structure:

```python
AudioClip(
    file="ambient_forest.wav",
    volume=0.8,
    pan=0.3,                # New: slight right bias
    delay=1.0,              # New: start after 1 second
    random_volume=0.15,     # New: ±15% volume variation
    random_pitch=0.5,       # New: ±0.5 semitone variation
    loop=True,
    fade_in=2.0,
    mqtt_triggers={"scene/forest": "play"}
)
```

## Implementation Priority

1. **Pan Control** - Immediate value, simple implementation
2. **Delay** - Critical for timing, moderate complexity
3. **Random Volume** - High impact for realism, simple implementation
4. **Random Pitch** - Nice-to-have, requires audio processing


## Backward Compatibility

All new parameters have sensible defaults that maintain existing behavior:
- `pan=0.0` (center, no change)
- `delay=0.0` (immediate, no change)
- `random_volume=0.0` (no variation, no change)
- `random_pitch=0.0` (no variation, no change)

Existing AudioClip configurations continue working unchanged.


## Technical Considerations

### Pan Implementation
- Use cosine/sine curves for smooth amplitude transitions
- Preserve total energy across stereo field
- Apply before volume scaling

### Delay Implementation
- Non-blocking timer threads
- Respect stop commands during delay period
- Handle MQTT reconnection during delay

### Random Variation
- Seed random generator for repeatability if needed
- Apply variations at playback time, not registration
- Clamp results to valid ranges

### Performance Impact
- Minimal overhead for unused features
- Random calculations only when needed
- No impact on existing deterministic playback 
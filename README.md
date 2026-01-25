# Gesture Control Orb Collector

A gesture-controlled orb collection game using computer vision, hand tracking, and head movement. Move the drone with your hand, make a fist to trigger a pulse, and use head movements to change modes and recharge energy.

## Quick Setup

### Prerequisites
- Python 3.11+
- Camera (built-in or USB webcam)

### Installation

```bash
# Clone repository
git clone <repository-url>
cd Shooter

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## How to Play

### Launch Game
```bash
python play.py          # Quick start
python main.py game     # Full game with options
python main.py debug    # Debug mode with visual feedback
```

### Gesture Controls
- **Move**: Move your hand to steer the drone
- **Pulse**: Make a fist to emit a pulse
- **Change Mode**: Tilt head left/right to cycle pulse modes
- **Recharge**: Nod head up/down to recharge energy
- **Rotate**: Turn head to rotate the drone

Inputs use a deadzone so small movements are ignored until you cross the threshold.

### Keyboard Fallback
When gesture recognition is unavailable or disabled:
- **WASD / Arrow Keys**: Move
- **Space**: Pulse
- **R**: Recharge
- **Q / E**: Change mode
- **P**: Pause
- **ESC**: Quit game

## Additional Options

```bash
# Performance settings
python main.py game --fps 30              # Set target FPS
python main.py game --resolution 640 480  # Set camera resolution

# Camera selection
python main.py game --camera-index 1      # Use different camera

# Debug mode
python main.py debug                      # Visual debug information
python main.py monitor                    # Camera preview with minimal overlays
```

## Troubleshooting

**Camera not detected:**
```bash
python main.py debug --camera-index 1   # Try different camera
```

**Low performance:**
```bash
python main.py game --fps 20 --resolution 480 360
```

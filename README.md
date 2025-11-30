# Shooter

Simple 2D shooter: control crosshair with your hand (via webcam & MediaPipe), shoot zombies before they reach you.

## Quick Start

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py --debug
```

## Requirements

- Python 3.11+
- Camera (webcam)



## Main Gestures

- **Palm rotation around axis** — activates/deactivates control (toggle ON/OFF)
- **Hand movement relative to calibration center** — moves the crosshair (virtual joystick)
- **Fist gesture** — shoots
- **Head rotation (left/right/tilt/nod)** — auxiliary control (future/optional)


## Usage

1. Clone the repo & set up the virtual environment (see Quick Start)
2. Run: `python run.py --debug`
3. Show your hand to the camera
4. Rotate your palm to toggle control ON/OFF (activation)
5. Move your hand to control the crosshair
6. Make a fist to shoot
7. (Optional) Use head rotation for auxiliary control
8. Press ESC to exit

## Options

- `python run.py --help` — all options
- `--camera-id N` — select camera
- `--fps N` — set FPS
- `--resolution W H` — set resolution

## Troubleshooting

- Use Python 3.11, activate venv
- Try different camera id if not working
- Lower resolution for better performance

## Config

Edit `hand_control/core/config.py` for advanced settings (sensitivity, camera, UI).

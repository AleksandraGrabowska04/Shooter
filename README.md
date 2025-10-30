# Shooter
A simple 2D pixel-art arcade shooter where the player controls a crosshair using hand movements detected by a webcam (via MediaPipe) and shoots approaching zombies before they reach the player.

# Prepare Environment

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

# Run the Application

```bash
source venv/bin/activate
python3.11 computer_vision.py
```
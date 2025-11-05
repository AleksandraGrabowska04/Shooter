# Shooter

A simple 2D pixel-art arcade shooter where the player controls a crosshair using hand movements detected by a webcam (via MediaPipe) and shoots approaching zombies before they reach the player.

## ⚡ Quick Start

```bash
# Create virtual environment with Python 3.11
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run
python run.py
```

## 📋 Requirements

- **Python 3.11+**
- **Camera (built-in or USB)**
- **MediaPipe, OpenCV, NumPy**
- **Virtual environment**

## 🎯 Gestures

- **✊ Fist** - System calibration and activation
- **👈👉 Tilts** - Turn left/right control
- **☝️👇 Positions** - Up/down movement control
- **👊 Thumb to Index** - 🔥 SHOOT! (when thumb touches the index finger)

## ⚙️ Launch Options

```bash
# Activate virtual environment first
source venv/bin/activate

# Show all options
python run.py --help

# Debug mode with visualization
python run.py --debug

# Camera selection
python run.py --camera-id 1

# FPS (default 30)
python run.py --fps 60

# Resolution (default 640x480)
python run.py --resolution 1920 1080
```

## 🏗️ Architecture

```
hand_control

├── core/           # Core modules (config, interfaces, system)
├── vision/         # Computer vision (MediaPipe)
├── gestures/       # Gesture recognition
├── ui/             # Visualization (OpenCV)
└── utils/          # Utilities (factory, exceptions)
```

## 🚀 Usage

1. **Clone repository:**

   ```bash
   git clone https://github.com/AleksandraGrabowska04/Shooter.git
   cd Shooter
   ```

2. **Set up Python 3.11 environment:**

   ```bash
   # Install Python 3.11 if not available

   # Create virtual environment
   python3.11 -m venv venv
   
   # Activate virtual environment
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run system:**

   ```bash
   python run.py
   ```

5. **Controls:**

   - Show hand to camera
   - Make fist ✊ for calibration
   - Show hand to camera
   - Control with gestures
   - Press `ESC` to exit

6. **Deactivate environment when done:**

   ```bash
   deactivate
   ```

## 🛠 Virtual Environment Management

```bash
# Activate environment (every time you work on project)
source venv/bin/activate

# Check Python version
python --version

# Install new packages
pip install package_name

# Update requirements.txt
pip freeze > requirements.txt

# Deactivate when done
deactivate
```

## 📝 Logging

System uses structured logging with different levels. In `--debug` mode shows detailed component operation information.

## 🔧 Configuration

All settings are in `hand_control/core/config.py`. Can configure:

- Gesture recognition sensitivity
- Camera settings (resolution, FPS)
- Gesture recognition sensitivity
- Visualization parameters
- Key thresholds

## ⚡ Troubleshooting

### Python Version Issues
```bash
# Check which Python you're using
which python
python --version

# If not Python 3.11, reactivate virtual environment
source venv/bin/activate
```

### Camera Issues
```bash
# Test camera access
python run.py --camera-id 0  # Try camera 0
python run.py --camera-id 1  # Try camera 1
```

### Package Installation Issues
```bash
# Reinstall packages
pip install --upgrade pip
pip install -r requirements.txt --upgrade
```

### Performance Issues
```bash
# Lower resolution for better performance
python run.py --resolution 320 240 --fps 15
```

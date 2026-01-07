#!/usr/bin/env python3
"""
Quick Game Launcher - Direct access to the demo game
====================================================

Simple launcher script for immediate game access without command line options.

Usage:
    python play.py       # Start the game immediately
"""

import sys
from main import main as main_app

if __name__ == "__main__":
    # Override sys.argv to force game mode
    original_argv = sys.argv.copy()
    sys.argv = [sys.argv[0], "game"]
    
    try:
        main_app()
    except KeyboardInterrupt:
        print("\n👋 Game stopped by user")
    except Exception as e:
        print(f"❌ Game error: {e}")
        sys.exit(1)
    finally:
        # Restore original argv
        sys.argv = original_argv

#!/usr/bin/env python3.11
"""
Hand Control System - Main Entry Point
=====================================

Run gesture-based hand control system with clean modular architecture.

Usage:
    python run.py              # Start with default settings
    python run.py --debug      # Enable debug visualization
    python run.py --help       # Show all options
"""

import argparse
import sys
import logging
from hand_control.core import create_hand_control_system, ApplicationConfig
from hand_control.utils.factory import DefaultLogger


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Hand Control System')
    parser.add_argument(
        '--debug', 
        action='store_true', 
        help='Enable debug mode with visualization'
    )
    parser.add_argument(
        '--camera-id', 
        type=int, 
        default=0, 
        help='Camera device ID (default: 0)'
    )
    parser.add_argument(
        '--fps', 
        type=int, 
        default=30, 
        help='Target FPS (default: 30)'
    )
    parser.add_argument(
        '--resolution', 
        nargs=2, 
        type=int, 
        default=[640, 480], 
        metavar=('WIDTH', 'HEIGHT'),
        help='Camera resolution (default: 640 480)'
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='[%(levelname)s] %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("🎮 Starting Hand Control System...")
    
    try:
        # Create configuration
        config = ApplicationConfig()
        
        # Apply command line options
        config.enable_debug_mode = args.debug
        config.camera.camera_index = args.camera_id
        config.camera.fps = args.fps
        config.camera.width = args.resolution[0]
        config.camera.height = args.resolution[1]
        
        # Show debug info if enabled
        config.ui.show_landmarks = args.debug
        config.ui.show_debug_info = args.debug
        
        logger.info(f"📷 Camera: Device {config.camera.camera_index}, "
                   f"{config.camera.width}x{config.camera.height} @ {config.camera.fps}fps")
        
        if config.enable_debug_mode:
            logger.info("🔧 Debug mode enabled - showing visualization")
        
        # Create logger instance
        system_logger = DefaultLogger("HandControlSystem", config)
        
        # Create and run system
        system = create_hand_control_system(config, system_logger)
        
        logger.info("🚀 System initialized successfully")
        if system.initialize():
            system.run()
        else:
            logger.error("❌ Failed to initialize system")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("👋 Shutting down gracefully...")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
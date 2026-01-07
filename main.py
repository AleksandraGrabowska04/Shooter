#!/usr/bin/env python3
"""
Hand Control System - Entry Point
=================================

Modes:
    monitor     - Lightweight monitoring with camera preview
    game        - Full integrated game experience
    debug       - Debug monitoring with visual feedback

Usage:
    python main.py monitor           # Monitoring mode (default)
    python main.py game              # Full game experience
    python main.py debug             # Debug mode with visuals
    python main.py --help            # Show all options
    python play.py                   # Quick game launcher
"""

import argparse
import sys
import logging
from hand_control.constants import DEFAULT_CAMERA_WIDTH, DEFAULT_CAMERA_HEIGHT, DEFAULT_FPS
from hand_control.core import create_hand_control_system, ApplicationConfig
from hand_control.utils.factory import DefaultLogger


def run_monitor_mode(config: ApplicationConfig, logger) -> None:
    """Run console monitoring mode."""
    print("Starting Hand Control Console Monitor...")
    print("Note: A camera preview window will open. Use Ctrl+C to exit.")
    
    try:
        config.enable_debug_mode = False
        config.ui.show_debug_info = False
        config.ui.show_landmarks = False

        system = create_hand_control_system(config, logger)
        if system.initialize():
            system.run()
        else:
            logger.error("Failed to initialize hand control system")
            
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped by user")
    except Exception as e:
        logger.error(f"Error in monitor mode: {e}")
        raise


def run_game_mode(config: ApplicationConfig, logger) -> None:
    """Run full integrated game experience."""
    print("Starting Hand Control Game Mode...")
    
    try:
        # Use GameEngine directly for better performance
        from game.game_engine import GameEngine
        engine = GameEngine(config, "collector")
        
        if engine.initialize():
            logger.info("Game engine initialized successfully")
            engine.run()
        else:
            logger.error("Failed to initialize game engine")
            
    except Exception as e:
        logger.error(f"Error in game mode: {e}")
        raise


def run_debug_mode(config: ApplicationConfig, logger) -> None:
    """Run debug mode with visual feedback."""
    print("Starting Hand Control Debug Mode...")
    
    try:
        # Enable debug settings
        config.enable_debug_mode = True
        config.ui.show_debug_info = True
        config.ui.show_landmarks = True
        
        system = create_hand_control_system(config, logger)
        if system.initialize():
            system.run()
        else:
            logger.error("Failed to initialize hand control system")
            
    except KeyboardInterrupt:
        print("\n👋 Debug mode stopped by user")
    except Exception as e:
        logger.error(f"Error in debug mode: {e}")
        raise


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Hand Control System - Entry Point",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py monitor           # Monitor (default)
  python main.py game              # Full game experience
  python main.py debug             # Debug mode with visuals
  python main.py game --fps 60    # Game at 60fps
  python play.py                   # Quick game start
        """
    )
    
    # Mode selection (positional argument)
    parser.add_argument(
        'mode',
        nargs='?',
        choices=['monitor', 'game', 'debug'],
        default='monitor',
        help='Operating mode: monitor (camera preview), game (full game), debug (visual debug)'
    )
    
    # Camera settings
    parser.add_argument(
        '--fps',
        type=int,
        default=DEFAULT_FPS,
        help=f'Target FPS for hand tracking (default: {DEFAULT_FPS})'
    )
    parser.add_argument(
        '--resolution',
        nargs=2,
        type=int,
        default=[DEFAULT_CAMERA_WIDTH, DEFAULT_CAMERA_HEIGHT],
        metavar=('WIDTH', 'HEIGHT'),
        help=f'Camera resolution (default: {DEFAULT_CAMERA_WIDTH} {DEFAULT_CAMERA_HEIGHT})'
    )
    
    # System settings
    parser.add_argument(
        '--camera-index',
        type=int,
        default=0,
        help='Camera device index (default: 0)'
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Setup logging based on mode
    if args.mode == 'debug':
        log_level = logging.DEBUG
    elif args.mode == 'monitor':
        log_level = logging.INFO  
    else:  # game mode
        log_level = logging.WARNING  # Less verbose for game
        
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create configuration
    config = ApplicationConfig()
    
    # Apply command line overrides
    config.camera.fps = args.fps
    config.camera.width = args.resolution[0]
    config.camera.height = args.resolution[1]
    config.camera.camera_index = args.camera_index
    
    # Create logger
    logger = DefaultLogger(name="hand_control_app", config=config)
    
    # Run the selected mode
    try:
        if args.mode == 'monitor':
            run_monitor_mode(config, logger)
        elif args.mode == 'game':
            run_game_mode(config, logger)
        elif args.mode == 'debug':
            run_debug_mode(config, logger)
        else:
            print(f"Unknown mode: {args.mode}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

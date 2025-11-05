"""
Configuration loader for handling file I/O and environment variables.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

from .application_config import ApplicationConfig
from .camera_config import CameraConfig
from .gesture_config import GestureConfig
from .ui_config import UIConfig
from .logging_config import LoggingConfig
from .performance_config import PerformanceConfig


class ConfigLoader:
    """
    Handles loading and saving configuration from/to various sources.
    """
    
    @staticmethod
    def from_file(config_path: str) -> ApplicationConfig:
        """
        Load configuration from JSON file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            ApplicationConfig instance
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid
        """
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_file, 'r') as f:
                data = json.load(f)
            
            # Create nested configurations
            camera_config = CameraConfig(**data.get('camera', {}))
            gesture_config = GestureConfig(**data.get('gestures', {}))
            ui_config = UIConfig(**data.get('ui', {}))
            logging_config = LoggingConfig(**data.get('logging', {}))
            performance_config = PerformanceConfig(**data.get('performance', {}))
            
            # Create main config
            app_data = data.get('application', {})
            return ApplicationConfig(
                camera=camera_config,
                gestures=gesture_config,
                ui=ui_config,
                logging=logging_config,
                performance=performance_config,
                enable_debug_mode=app_data.get('enable_debug_mode', False),
                auto_calibrate=app_data.get('auto_calibrate', True),
                exit_key=app_data.get('exit_key', 27)  # ESC key
            )
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise ValueError(f"Error loading configuration: {e}")
    
    @staticmethod
    def to_file(config: ApplicationConfig, config_path: str) -> None:
        """
        Save configuration to JSON file.
        
        Args:
            config: ApplicationConfig instance to save
            config_path: Path where to save configuration
        """
        config_data = config.to_dict()
        
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=4)
    
    @staticmethod
    def get_environment_overrides() -> Dict[str, Any]:
        """
        Get configuration overrides from environment variables.
        
        Returns:
            Dictionary of configuration overrides
        """
        overrides = {}
        
        # Camera settings
        if 'HAND_CONTROL_CAMERA_WIDTH' in os.environ:
            overrides['camera_width'] = int(os.environ['HAND_CONTROL_CAMERA_WIDTH'])
        if 'HAND_CONTROL_CAMERA_HEIGHT' in os.environ:
            overrides['camera_height'] = int(os.environ['HAND_CONTROL_CAMERA_HEIGHT'])
        if 'HAND_CONTROL_CAMERA_INDEX' in os.environ:
            overrides['camera_index'] = int(os.environ['HAND_CONTROL_CAMERA_INDEX'])
            
        # Debug settings
        if 'HAND_CONTROL_DEBUG' in os.environ:
            overrides['enable_debug_mode'] = os.environ['HAND_CONTROL_DEBUG'].lower() == 'true'
            
        # Logging settings
        if 'HAND_CONTROL_LOG_LEVEL' in os.environ:
            overrides['log_level'] = os.environ['HAND_CONTROL_LOG_LEVEL'].upper()
            
        return overrides
    
    @staticmethod
    def apply_overrides(config: ApplicationConfig, overrides: Dict[str, Any]) -> None:
        """
        Apply configuration overrides to a config instance.
        
        Args:
            config: ApplicationConfig instance to modify
            overrides: Dictionary of configuration overrides
        """
        if 'camera_width' in overrides:
            config.camera.width = overrides['camera_width']
        if 'camera_height' in overrides:
            config.camera.height = overrides['camera_height']
        if 'camera_index' in overrides:
            config.camera.camera_index = overrides['camera_index']
        if 'enable_debug_mode' in overrides:
            config.enable_debug_mode = overrides['enable_debug_mode']
        if 'log_level' in overrides:
            config.logging.level = overrides['log_level']


def load_config(config_path: Optional[str] = None) -> ApplicationConfig:
    """
    Load application configuration from file or create default.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        ApplicationConfig instance
        
    Raises:
        ValueError: If configuration validation fails
    """
    if config_path and Path(config_path).exists():
        config = ConfigLoader.from_file(config_path)
    else:
        config = ApplicationConfig()
    
    # Apply environment overrides
    overrides = ConfigLoader.get_environment_overrides()
    if overrides:
        ConfigLoader.apply_overrides(config, overrides)
    
    # Validate configuration
    errors = config.validate()
    if errors:
        raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    return config
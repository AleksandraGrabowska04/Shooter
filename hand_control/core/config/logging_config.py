"""
Logging configuration settings.
"""

from dataclasses import dataclass


@dataclass 
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    enable_file_logging: bool = False
    log_file_path: str = "hand_control.log"
    enable_performance_logging: bool = False
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    def __post_init__(self):
        """Validate logging configuration after initialization."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.level.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        
        # Normalize log level to uppercase
        self.level = self.level.upper()
        
        if self.enable_file_logging and not self.log_file_path:
            raise ValueError("Log file path must be specified when file logging is enabled")
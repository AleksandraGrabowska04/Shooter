"""
Configuration validation utilities.
"""

from typing import List, Dict, Any

from .application_config import ApplicationConfig


class ConfigValidator:
    """
    Provides advanced validation utilities for configuration.
    """
    
    @staticmethod
    def validate_comprehensive(config: ApplicationConfig) -> Dict[str, List[str]]:
        """
        Perform comprehensive validation of configuration.
        
        Args:
            config: ApplicationConfig instance to validate
            
        Returns:
            Dictionary mapping component names to lists of error messages
        """
        validation_results = {
            'camera': [],
            'gestures': [],
            'ui': [],
            'logging': [],
            'performance': [],
            'application': []
        }
        
        # Camera validation
        try:
            config.camera.__post_init__()
        except ValueError as e:
            validation_results['camera'].append(str(e))
        
        # Additional camera checks
        if config.camera.width > 4000 or config.camera.height > 3000:
            validation_results['camera'].append("Camera resolution seems unusually high")
        if config.camera.fps > 120:
            validation_results['camera'].append("Camera FPS seems unusually high")
        
        # Gesture validation
        try:
            config.gestures.__post_init__()
        except ValueError as e:
            validation_results['gestures'].append(str(e))
        
        # Additional gesture checks
        if config.gestures.calibration_frames > 100:
            validation_results['gestures'].append("Calibration frames count seems excessive")
        
        # UI validation
        try:
            config.ui.__post_init__()
        except ValueError as e:
            validation_results['ui'].append(str(e))
        
        # Logging validation
        try:
            config.logging.__post_init__()
        except ValueError as e:
            validation_results['logging'].append(str(e))
        
        # Performance validation
        try:
            config.performance.__post_init__()
        except ValueError as e:
            validation_results['performance'].append(str(e))
        
        # Application-level validation
        if config.exit_key < 0 or config.exit_key > 255:
            validation_results['application'].append("Exit key code must be between 0 and 255")
        
        return validation_results
    
    @staticmethod
    def get_recommendations(config: ApplicationConfig) -> List[str]:
        """
        Get performance and usability recommendations for configuration.
        
        Args:
            config: ApplicationConfig instance to analyze
            
        Returns:
            List of recommendation messages
        """
        recommendations = []
        
        # Camera recommendations
        if config.camera.width * config.camera.height > 1920 * 1080:
            recommendations.append("Consider lowering camera resolution for better performance")
        
        if config.camera.fps > 60:
            recommendations.append("FPS higher than 60 may not provide significant benefits")
        
        # Gesture recommendations
        if config.gestures.motion_smoothing < 0.2:
            recommendations.append("Low motion smoothing may cause jittery detection")
        
        if config.gestures.fist_confidence_threshold < 0.5:
            recommendations.append("Low fist confidence threshold may cause false positives")
        
        # UI recommendations
        if config.ui.show_landmarks and config.ui.show_debug_info:
            recommendations.append("Showing both landmarks and debug info may clutter the display")
        
        # Performance recommendations
        if not config.performance.enable_metrics and config.enable_debug_mode:
            recommendations.append("Consider enabling performance metrics in debug mode")
        
        return recommendations
    
    @staticmethod
    def check_compatibility(config: ApplicationConfig) -> List[str]:
        """
        Check for configuration compatibility issues.
        
        Args:
            config: ApplicationConfig instance to check
            
        Returns:
            List of compatibility warning messages
        """
        warnings = []
        
        # Check for conflicting settings
        if config.enable_debug_mode and not config.ui.show_debug_info:
            warnings.append("Debug mode is enabled but debug info display is disabled")
        
        if config.logging.enable_performance_logging and not config.performance.enable_metrics:
            warnings.append("Performance logging enabled but metrics collection is disabled")
        
        if config.performance.memory_monitoring and not config.performance.enable_metrics:
            warnings.append("Memory monitoring enabled but general metrics are disabled")
        
        return warnings
"""
Mathematical utility functions for gesture processing.
"""

from typing import Dict, Tuple, Any, Optional


def quantize_landmarks(landmarks: Dict[str, Any], position_step: float = 5.0) -> Dict[str, Any]:
    """
    Quantize landmarks to reduce jittering in gesture detection.
    
    Args:
        landmarks: Dictionary of landmark positions
        position_step: Step size for quantization (pixels)
        
    Returns:
        Dictionary with quantized landmark positions
    """
    if not landmarks:
        return landmarks
    
    quantized = {}
    
    for key, position in landmarks.items():
        if position and len(position) >= 3:
            # Quantize each coordinate
            quantized_pos = (
                round(position[0] / position_step) * position_step,
                round(position[1] / position_step) * position_step,
                round(position[2] / position_step) * position_step
            )
            quantized[key] = quantized_pos
        else:
            quantized[key] = position
    
    return quantized


def quantize_value(value: float, step: float) -> float:
    """
    Quantize a single value to the nearest step.
    
    Args:
        value: Value to quantize
        step: Step size for quantization
        
    Returns:
        Quantized value
    """
    return round(value / step) * step


def calculate_distance_2d(point1: Tuple[float, float], 
                         point2: Tuple[float, float]) -> float:
    """
    Calculate 2D Euclidean distance between two points.
    
    Args:
        point1: First point (x, y)
        point2: Second point (x, y)
        
    Returns:
        Distance between points
    """
    import math
    return math.sqrt(
        (point1[0] - point2[0]) ** 2 +
        (point1[1] - point2[1]) ** 2
    )


def calculate_distance_3d(point1: Tuple[float, float, float], 
                         point2: Tuple[float, float, float]) -> float:
    """
    Calculate 3D Euclidean distance between two points.
    
    Args:
        point1: First point (x, y, z)
        point2: Second point (x, y, z)
        
    Returns:
        Distance between points
    """
    import math
    return math.sqrt(
        (point1[0] - point2[0]) ** 2 +
        (point1[1] - point2[1]) ** 2 +
        (point1[2] - point2[2]) ** 2
    )


def calculate_angle_rad(vector1: Tuple[float, float, float], 
                       vector2: Tuple[float, float, float]) -> float:
    """
    Calculate angle in radians between two 3D vectors.
    
    Args:
        vector1: First vector (x, y, z)
        vector2: Second vector (x, y, z)
        
    Returns:
        Angle in radians
    """
    import math
    
    # Calculate dot product
    dot_product = (vector1[0] * vector2[0] + 
                   vector1[1] * vector2[1] + 
                   vector1[2] * vector2[2])
    
    # Calculate magnitudes
    mag1 = math.sqrt(vector1[0]**2 + vector1[1]**2 + vector1[2]**2)
    mag2 = math.sqrt(vector2[0]**2 + vector2[1]**2 + vector2[2]**2)
    
    if mag1 == 0 or mag2 == 0:
        return 0.0
    
    # Calculate angle
    cos_angle = dot_product / (mag1 * mag2)
    cos_angle = max(-1.0, min(1.0, cos_angle))  # Clamp to valid range
    
    return math.acos(cos_angle)


def normalize_confidence(value: float, 
                        min_threshold: float, 
                        max_threshold: float) -> float:
    """
    Normalize a value to confidence score between 0.0 and 1.0.
    
    Args:
        value: Raw value to normalize
        min_threshold: Minimum threshold value
        max_threshold: Maximum threshold value
        
    Returns:
        Normalized confidence score (0.0 to 1.0)
    """
    if value <= min_threshold:
        return 0.0
    elif value >= max_threshold:
        return 1.0
    else:
        return (value - min_threshold) / (max_threshold - min_threshold)


def clamp_confidence(value: float) -> float:
    """
    Clamp confidence value to valid range [0.0, 1.0].
    
    Args:
        value: Raw confidence value
        
    Returns:
        Clamped confidence between 0.0 and 1.0
    """
    return max(0.0, min(1.0, value))
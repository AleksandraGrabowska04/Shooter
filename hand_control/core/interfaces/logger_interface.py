"""
Logger interface definition.
"""

from abc import ABC, abstractmethod


class ILogger(ABC):
    """Interface for logging functionality"""
    
    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        """
        Log debug message.
        
        Args:
            message: Debug message to log
            **kwargs: Additional context data
        """
        pass
    
    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        """
        Log info message.
        
        Args:
            message: Info message to log
            **kwargs: Additional context data
        """
        pass
    
    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        """
        Log warning message.
        
        Args:
            message: Warning message to log
            **kwargs: Additional context data
        """
        pass
    
    @abstractmethod
    def error(self, message: str, **kwargs) -> None:
        """
        Log error message.
        
        Args:
            message: Error message to log
            **kwargs: Additional context data
        """
        pass
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypeVar, Generic

from ..schema import Workout


class ParseError(Exception):
    """Exception raised when parsing fails."""
    pass


T = TypeVar('T')


class BaseParser(ABC, Generic[T]):
    """
    Base class for all workout format parsers.
    
    Parsers can implement one or both directions:
    - from_format: Convert from external format to Structured Workout Format
    - to_format: Convert from Structured Workout Format to external format
    """
    
    @property
    @abstractmethod
    def format_name(self) -> str:
        """Human-readable name of the format this parser handles."""
        pass
    
    @property
    @abstractmethod
    def file_extensions(self) -> list[str]:
        """List of file extensions this parser can handle (e.g., ['.txt', '.json'])."""
        pass
    
    def supports_import(self) -> bool:
        """Return True if this parser can convert FROM the external format TO SWF."""
        return hasattr(self, 'from_format') and callable(getattr(self, 'from_format'))
    
    def supports_export(self) -> bool:
        """Return True if this parser can convert FROM SWF TO the external format."""
        return hasattr(self, 'to_format') and callable(getattr(self, 'to_format'))
    
    def from_format(self, data: T, variables: Optional[Dict[str, Any]] = None) -> Workout:
        """
        Convert from external format to Structured Workout Format.
        
        Args:
            data: The input data in the external format
            variables: Optional variable substitutions
            
        Returns:
            Workout instance
            
        Raises:
            NotImplementedError: If this parser doesn't support import
            ParseError: If parsing fails
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support importing from {self.format_name}")
    
    def to_format(self, workout: Workout, **kwargs) -> T:
        """
        Convert from Structured Workout Format to external format.
        
        Args:
            workout: The Workout instance to convert
            **kwargs: Format-specific options
            
        Returns:
            Data in the external format
            
        Raises:
            NotImplementedError: If this parser doesn't support export
            ParseError: If conversion fails
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support exporting to {self.format_name}")
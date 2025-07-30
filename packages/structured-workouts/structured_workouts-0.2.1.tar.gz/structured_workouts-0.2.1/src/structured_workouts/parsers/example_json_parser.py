import json
from typing import Any, Dict, Optional

from .base import BaseParser, ParseError
from ..schema import Workout
from ..base import Interval, ConstantValue, Value, Reference, VolumeQuantity, IntensityQuantity


class ExampleJSONParser(BaseParser[dict]):
    """
    Example parser for a hypothetical JSON workout format.
    
    This demonstrates how to create a parser that only supports one direction.
    This parser only supports importing FROM JSON TO SWF.
    """
    
    @property
    def format_name(self) -> str:
        return "Example JSON Format"
    
    @property
    def file_extensions(self) -> list[str]:
        return ['.json']
    
    def from_format(self, data: dict, variables: Optional[Dict[str, Any]] = None) -> Workout:
        """
        Parse example JSON format to SWF.
        
        Expected JSON structure:
        {
            "name": "Workout Name",
            "intervals": [
                {"duration_min": 10, "intensity_pct": 60},
                {"duration_min": 5, "intensity_pct": 85}
            ]
        }
        """
        try:
            title = data.get('name')
            intervals_data = data.get('intervals', [])
            
            content = []
            for interval_data in intervals_data:
                duration = interval_data.get('duration_min')
                intensity_pct = interval_data.get('intensity_pct')
                
                if duration is None or intensity_pct is None:
                    raise ParseError("Missing duration_min or intensity_pct in interval")
                
                volume = ConstantValue(value=Value(reference=Reference.absolute, value=duration), quantity=VolumeQuantity.duration)
                intensity = ConstantValue(value=Value(reference=Reference.absolute, value=intensity_pct / 100), quantity=IntensityQuantity.power)
                
                content.append(Interval(volume=volume, intensity=intensity))
            
            return Workout(title=title, content=content)
            
        except (KeyError, TypeError, ValueError) as e:
            raise ParseError(f"Failed to parse JSON format: {e}")
    
    # Note: This parser doesn't implement to_format(), so it only supports import
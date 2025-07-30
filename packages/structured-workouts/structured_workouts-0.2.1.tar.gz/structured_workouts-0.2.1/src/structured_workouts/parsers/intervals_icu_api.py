import json
from typing import Any, Dict, Optional

from .base import BaseParser, ParseError
from .intervals_icu_text import IntervalsICUTextParser
from ..schema import Workout


class IntervalsICUAPIParser(BaseParser[str]):
    """
    Parser for Intervals.icu API JSON format.
    
    This parser handles the JSON format returned by the Intervals.icu API for workouts.
    The API format includes metadata fields and uses the 'description' field to store
    the native Intervals.icu text format workout definition.
    
    ASSUMPTIONS AND SHORTCUTS:
    
    1. **Primary workout data source**: We primarily extract workout structure from the 
       'description' field which contains the native Intervals.icu text format. This 
       leverages our existing IntervalsICUTextParser.
    
    2. **Metadata handling**: We preserve API metadata (id, name, athlete_id, etc.) but 
       only use 'name' as the workout title in our SWF. Other fields like folder_id, 
       target, tags are ignored for simplicity.
    
    3. **workout_doc field**: The 'workout_doc' field contains structured workout data
       but its format is not fully documented in the API spec. We ignore this field
       and rely on the 'description' field instead.
    
    4. **Date/time fields**: Fields like 'updated', 'plan_applied' are preserved in 
       export but not used for workout structure conversion.
    
    5. **File attachments**: The 'attachments' array and file_contents fields are 
       ignored as they're not relevant to workout structure parsing.
    
    6. **Training metrics**: Fields like 'icu_training_load', 'joules', 'moving_time'
       are calculated values that we don't attempt to recreate.
    
    7. **Target types**: We convert the 'target' enum to a simple string but don't
       enforce validation against the API enum values.
    
    8. **Indoor flag**: We preserve the 'indoor' boolean but don't use it for 
       workout structure decisions.
    
    9. **Error handling**: If 'description' field is missing or empty, we create
       a minimal workout structure rather than failing completely.
    
    10. **Bi-directional limitations**: When exporting TO the API format, we create
        a valid API structure but many calculated fields (like joules, icu_training_load)
        will be None/empty and would need to be calculated by the API server.
    """
    
    @property
    def format_name(self) -> str:
        return "Intervals.icu API JSON"
    
    @property
    def file_extensions(self) -> list[str]:
        return ['.json']
    
    def __init__(self):
        # Use the text parser for handling the description field
        self._text_parser = IntervalsICUTextParser()
    
    def from_format(self, data: str, variables: Optional[Dict[str, Any]] = None) -> Workout:
        """
        Parse Intervals.icu API JSON format to SWF.
        
        WARNING: This import functionality is EXPERIMENTAL and not feature complete.
        The parser may not handle all intervals.icu API features correctly and makes
        several assumptions about the data format. Use with caution and verify results carefully.
        
        Args:
            data: JSON string representing the API workout
            variables: Optional variable substitutions
            
        Returns:
            Workout instance
            
        Raises:
            ParseError: If parsing fails
        """
        import warnings
        warnings.warn(
            "IntervalsICUAPIParser.from_format() is experimental and not feature complete. "
            "The parser may not handle all intervals.icu API features correctly and makes "
            "several assumptions about the data format. Use with caution and verify results carefully.",
            UserWarning,
            stacklevel=2
        )
        try:
            # Parse JSON string to dict
            if isinstance(data, str):
                workout_data = json.loads(data)
            else:
                workout_data = data
            # Extract the workout name (use 'name' field as title)
            title = workout_data.get('name', 'Intervals.icu Workout')
            
            # Extract the description field which contains the native workout format
            description_text = workout_data.get('description', '')
            
            if description_text and description_text.strip():
                # Parse the description using our text parser
                workout = self._text_parser.from_format(description_text, variables)
                # Override the title with the API name field
                workout.title = title
                return workout
            else:
                # No description available, create minimal workout
                return Workout(
                    title=title,
                    content=[]
                )
                
        except json.JSONDecodeError as e:
            raise ParseError(f"Invalid JSON in Intervals.icu API format: {e}")
        except Exception as e:
            raise ParseError(f"Failed to parse Intervals.icu API JSON: {e}")
    
    def to_format(self, workout: Workout, **kwargs) -> str:
        """
        Convert SWF to Intervals.icu API JSON format.
        
        Args:
            workout: Workout instance to convert
            **kwargs: Format options. Supported options:
                - athlete_id: str - The athlete ID for the workout
                - workout_id: int - The workout ID
                - folder_id: int - The folder/plan ID
                - target: str - Target type (AUTO, POWER, HR, PACE)
                - indoor: bool - Whether this is an indoor workout
                
        Returns:
            JSON string in Intervals.icu API format
        """
        # Convert workout back to text format for the description field
        description_text = self._text_parser.to_format(workout)
        
        # Build the API JSON structure
        api_json = {
            "name": workout.title or "Structured Workout",
            "description": description_text,
        }
        
        # Add optional fields from kwargs
        if "athlete_id" in kwargs:
            api_json["athlete_id"] = kwargs["athlete_id"]
        
        if "workout_id" in kwargs:
            api_json["id"] = kwargs["workout_id"]
            
        if "folder_id" in kwargs:
            api_json["folder_id"] = kwargs["folder_id"]
            
        if "target" in kwargs:
            # Validate target against known enum values
            valid_targets = ["AUTO", "POWER", "HR", "PACE"]
            target = kwargs["target"].upper()
            if target in valid_targets:
                api_json["target"] = target
        
        if "indoor" in kwargs:
            api_json["indoor"] = bool(kwargs["indoor"])
        
        # Set some reasonable defaults for API compatibility
        api_json.update({
            "type": "Workout",  # Generic workout type
            "hide_from_athlete": False,
            "for_week": False,
        })
        
        # Add workout description as additional context if available
        if workout.description:
            # Combine description with the generated text
            api_json["description"] = f"{description_text}\n\n# {workout.description}"
        
        return json.dumps(api_json, indent=2)
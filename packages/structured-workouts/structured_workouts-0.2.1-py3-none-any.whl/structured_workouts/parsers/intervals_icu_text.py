import re
from typing import Any, Dict, List, Optional, Union

from .base import BaseParser, ParseError
from ..schema import Workout
from ..base import (
    Interval, Repeat, Section, Instruction,
    ConstantValue, RangeValue, Value, Reference,
    VolumeQuantity, IntensityQuantity, RepeatQuantity
)


class IntervalsICUTextParser(BaseParser[str]):
    """
    Parser for Intervals.icu text format (workout builder format).
    
    Format example:
    Warmup
    - 20m 60%
    
    Main set 6x
    - 4m 100%, power is less important than getting the torque  
    - 5m recovery at 40%
    
    Cooldown
    - 20m 60%
    
    Percentages are relative to threshold power (handled as variables).
    """
    
    @property
    def format_name(self) -> str:
        return "Intervals.icu Text Format"
    
    @property
    def file_extensions(self) -> list[str]:
        return ['.txt']
    
    def from_format(self, data: str, variables: Optional[Dict[str, Any]] = None) -> Workout:
        """
        Parse Intervals.icu text format to SWF.
        
        WARNING: This import functionality is EXPERIMENTAL and not feature complete.
        The parser may not handle all intervals.icu text format features correctly.
        Use with caution and verify results carefully.
        
        Args:
            data: Text string in Intervals.icu format
            variables: Optional variable substitutions
            
        Returns:
            Workout instance
        """
        import warnings
        warnings.warn(
            "IntervalsICUTextParser.from_format() is experimental and not feature complete. "
            "The parser may not handle all intervals.icu text format features correctly. "
            "Use with caution and verify results carefully.",
            UserWarning,
            stacklevel=2
        )
        lines = [line.rstrip() for line in data.split('\n')]
        if not any(line.strip() for line in lines):
            raise ParseError("Empty workout data")
        
        content = []
        current_section = None
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
                
            if line.startswith('- '):
                # This is an interval line
                interval_or_instruction = self._parse_interval_line(line[2:])
                if current_section:
                    current_section.content.append(interval_or_instruction)
                else:
                    content.append(interval_or_instruction)
            else:
                # This is a section header, potentially with repeat count
                section_name, repeat_count = self._parse_section_header(line)
                
                if repeat_count:
                    # Create a repeat section
                    repeat_content = []
                    current_section = Section(name=section_name, content=repeat_content)
                    
                    # Parse the intervals for this repeat
                    i += 1
                    while i < len(lines) and lines[i].strip().startswith('- '):
                        interval_line = lines[i].strip()[2:]
                        interval_or_instruction = self._parse_interval_line(interval_line)
                        repeat_content.append(interval_or_instruction)
                        i += 1
                    
                    # Create the repeat structure
                    repeat = Repeat(
                        type="repeat",
                        count=ConstantValue(value=Value(reference=Reference.absolute, value=repeat_count), quantity=RepeatQuantity.NUMBER),
                        content=repeat_content
                    )
                    
                    content.append(Section(name=section_name, content=[repeat]))
                    current_section = None
                    continue
                else:
                    # Regular section
                    current_section = Section(name=section_name, content=[])
                    content.append(current_section)
            
            i += 1
        
        return Workout(title="Intervals.icu Workout", content=content)
    
    def to_format(self, workout: Workout, **kwargs) -> str:
        """
        Convert SWF to Intervals.icu text format.
        
        Args:
            workout: Workout instance to convert
            **kwargs: Format options
            
        Returns:
            Text string in Intervals.icu format
        """
        lines = []
        
        # Don't include title for intervals.icu format
        
        for i, item in enumerate(workout.content):
            if i > 0:
                lines.append("")  # Add empty line between sections
            item_text = self._format_item(item)
            if item_text:
                lines.append(item_text)
        
        return '\n'.join(lines)
    
    def _parse_section_header(self, line: str) -> tuple[str, Optional[int]]:
        """Parse section header and extract repeat count if present."""
        # Look for pattern like "Main set 6x"
        match = re.match(r'^(.+?)\s+(\d+)x\s*$', line)
        if match:
            return match.group(1).strip(), int(match.group(2))
        return line.strip(), None
    
    def _parse_interval_line(self, line: str) -> Union[Interval, Instruction]:
        """Parse an interval line or return as instruction if not parseable."""
        # Look for pattern like "20m 60%" or "4m 100%, power is less important than getting the torque"
        # Also handle "5m recovery at 40%"
        
        # First try the basic pattern with optional description
        match = re.match(r'^(\d+)m\s+(\d+)%(?:,\s*(.+))?$', line)
        if match:
            duration_minutes = int(match.group(1))
            percentage = int(match.group(2))
            description = match.group(3)
            
            # Create interval with threshold-relative intensity (convert minutes to seconds)
            volume = ConstantValue(value=Value(reference=Reference.absolute, value=duration_minutes * 60), quantity=VolumeQuantity.duration)
            intensity = ConstantValue(
                value=Value(reference=Reference.parameter, value=percentage / 100, parameter="threshold"),
                quantity=IntensityQuantity.power
            )
            
            interval = Interval(volume=volume, intensity=intensity)
            
            # If there's a description, we need to return both interval and instruction
            # For now, let's create a compound structure or just return the interval
            # and handle descriptions separately in a future enhancement
            if description:
                # For simplicity, create an instruction from the description
                return Instruction(text=f"{duration_minutes}m {percentage}%, {description}")
            
            return interval
        
        # Try pattern like "5m recovery at 40%"
        match = re.match(r'^(\d+)m\s+\w+\s+at\s+(\d+)%$', line)
        if match:
            duration_minutes = int(match.group(1))
            percentage = int(match.group(2))
            
            volume = ConstantValue(value=Value(reference=Reference.absolute, value=duration_minutes * 60), quantity=VolumeQuantity.duration)
            intensity = ConstantValue(
                value=Value(reference=Reference.parameter, value=percentage / 100, parameter="threshold"),
                quantity=IntensityQuantity.power
            )
            
            return Interval(volume=volume, intensity=intensity)
        
        # Treat as instruction if not parseable as interval
        return Instruction(text=line)
    
    def _format_item(self, item: Union[Interval, Repeat, Section, Instruction]) -> str:
        """Format workout item to text."""
        if isinstance(item, Instruction):
            return f"- {item.text}"
        elif isinstance(item, Section):
            lines = []
            
            # Check if this section contains a single repeat
            if len(item.content) == 1 and isinstance(item.content[0], Repeat):
                repeat = item.content[0]
                count = repeat.count.value.value if isinstance(repeat.count, ConstantValue) and repeat.count.value.reference == Reference.absolute else 1
                lines.append(f"{item.name} {count}x")
                for content_item in repeat.content:
                    lines.append(self._format_item(content_item))
            else:
                # Regular section
                if item.name:
                    lines.append(item.name)
                for content_item in item.content:
                    lines.append(self._format_item(content_item))
            
            return '\n'.join(lines)
        elif isinstance(item, Repeat):
            # This shouldn't normally be called directly as repeats are handled in sections
            lines = [
                f"{item.count.value.value}x"
            ]
            for content_item in item.content:
                lines.append(self._format_item(content_item))
            return '\n'.join(lines)
        elif isinstance(item, Interval):
            volume_text = self._format_volume(item.volume)
            intensity_text = self._format_intensity(item.intensity)
            return f"- {volume_text} {intensity_text}"
        
        return ""
    
    def _format_volume(self, volume) -> str:
        """Format volume specification."""
        if isinstance(volume, ConstantValue):
            value = volume.value.value
            if volume.quantity == VolumeQuantity.duration:
                # Convert seconds to minutes for intervals.icu format
                return f"{int(value / 60)}m"
            else:
                return f"{value}km"
        return "?m"
    
    def _format_intensity(self, intensity) -> str:
        """Format intensity specification."""
        if isinstance(intensity, ConstantValue):
            if intensity.value.reference == Reference.parameter and intensity.value.parameter == "threshold":
                return f"{int(intensity.value.value * 100)}%"
            elif intensity.value.reference == Reference.absolute:
                return f"{int(intensity.value.value)}W"
        elif isinstance(intensity, RangeValue):
            if intensity.min and intensity.max and intensity.min.reference == Reference.parameter and intensity.max.reference == Reference.parameter:
                min_pct = int(intensity.min.value * 100)
                max_pct = int(intensity.max.value * 100)
                return f"{min_pct}-{max_pct}%"
            elif intensity.min and intensity.max and intensity.min.reference == Reference.absolute and intensity.max.reference == Reference.absolute:
                return f"{int(intensity.min.value)}-{int(intensity.max.value)}W"
        
        return "60%"
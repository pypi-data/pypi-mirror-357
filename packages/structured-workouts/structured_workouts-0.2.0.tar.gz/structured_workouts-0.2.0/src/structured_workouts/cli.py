#!/usr/bin/env python3
"""
Command-line interface for structured-workouts.

This CLI allows conversion between different workout formats, with Structured Workout Format (SWF) 
as the default output format.
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Type, Optional

from .parsers.base import BaseParser
from .parsers import IntervalsICUTextParser, IntervalsICUAPIParser
from .schema import Workout


class ParserRegistry:
    """Registry of available parsers for different workout formats."""
    
    def __init__(self):
        self._parsers: Dict[str, Type[BaseParser]] = {}
        self._register_parsers()
    
    def _register_parsers(self):
        """Register all available parsers."""
        self.register("intervals-icu-text", IntervalsICUTextParser)
        self.register("intervals-icu-api", IntervalsICUAPIParser)
        # Add more parsers here as they're implemented
    
    def register(self, format_name: str, parser_class: Type[BaseParser]):
        """Register a parser for a specific format."""
        self._parsers[format_name] = parser_class
    
    def get_parser(self, format_name: str) -> BaseParser:
        """Get a parser instance for the specified format."""
        if format_name not in self._parsers:
            available = ", ".join(self._parsers.keys())
            raise ValueError(f"Unknown format '{format_name}'. Available formats: {available}")
        return self._parsers[format_name]()
    
    def get_available_formats(self) -> list[str]:
        """Get list of available format names."""
        return list(self._parsers.keys())
    
    def detect_format_from_extension(self, file_path: Path) -> Optional[str]:
        """Try to detect format from file extension."""
        extension = file_path.suffix.lower()
        
        for format_name, parser_class in self._parsers.items():
            parser = parser_class()
            if extension in parser.file_extensions:
                return format_name
        
        return None


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="structured-workouts",
        description="Convert between different structured workout formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert intervals.icu text to SWF JSON
  structured-workouts --from intervals-icu-text --from-file workout.txt
  
  # Convert intervals.icu text to SWF JSON and save to file
  structured-workouts --from intervals-icu-text --from-file workout.txt --output workout.json
  
  # Convert from intervals.icu text to another format (when more parsers are added)
  structured-workouts --from intervals-icu-text --from-file workout.txt --to intervals-icu-text
        """
    )
    
    # Required arguments (unless --list-formats is used)
    parser.add_argument(
        "--from", 
        dest="from_format",
        help="Source format (e.g., 'intervals-icu-text')"
    )
    
    parser.add_argument(
        "--from-file", 
        dest="from_file",
        type=Path,
        help="Path to the source file"
    )
    
    # Optional arguments
    parser.add_argument(
        "--to", 
        dest="to_format",
        default="swf",
        help="Target format (default: 'swf' for Structured Workout Format JSON)"
    )
    
    parser.add_argument(
        "--output", "-o",
        dest="output_file",
        type=Path,
        help="Output file path (default: print to stdout)"
    )
    
    parser.add_argument(
        "--list-formats",
        action="store_true",
        help="List all available formats and exit"
    )
    
    parser.add_argument(
        "--variables",
        type=str,
        help="JSON string of variables for parsing (e.g., '{\"threshold\": 250}')"
    )
    
    return parser


def list_formats(registry: ParserRegistry):
    """List all available formats with their details."""
    print("Available formats:")
    print()
    
    # Special case for SWF
    print("  swf")
    print("    Name: Structured Workout Format (SWF)")
    print("    Extensions: .swf.json")
    print("    Import: No (native format)")
    print("    Export: Yes (default)")
    print()
    
    # List all registered parsers
    for format_name in sorted(registry.get_available_formats()):
        parser = registry.get_parser(format_name)
        extensions = ", ".join(parser.file_extensions)
        
        print(f"  {format_name}")
        print(f"    Name: {parser.format_name}")
        print(f"    Extensions: {extensions}")
        print(f"    Import: {'Yes' if parser.supports_import() else 'No'}")
        print(f"    Export: {'Yes' if parser.supports_export() else 'No'}")
        print()


def convert_workout(
    from_format: str,
    from_file: Path,
    to_format: str,
    variables: Optional[dict] = None
) -> str:
    """Convert a workout from one format to another."""
    registry = ParserRegistry()
    
    # Validate source file exists
    if not from_file.exists():
        raise FileNotFoundError(f"Source file not found: {from_file}")
    
    # Get source parser
    if from_format == "swf":
        raise ValueError("Cannot import from SWF format (use --from with a specific parser format)")
    
    source_parser = registry.get_parser(from_format)
    if not source_parser.supports_import():
        raise ValueError(f"Format '{from_format}' does not support importing")
    
    # Read and parse source file
    with open(from_file, 'r', encoding='utf-8') as f:
        source_data = f.read()
    
    workout = source_parser.from_format(source_data, variables=variables)
    
    # Convert to target format
    if to_format == "swf":
        # Output as SWF JSON
        return workout.model_dump_json(indent=2)
    else:
        # Use target parser
        target_parser = registry.get_parser(to_format)
        if not target_parser.supports_export():
            raise ValueError(f"Format '{to_format}' does not support exporting")
        
        return target_parser.to_format(workout)


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    registry = ParserRegistry()
    
    # Handle --list-formats
    if args.list_formats:
        list_formats(registry)
        return
    
    # Validate required arguments when not listing formats
    if not args.from_format:
        print("Error: --from is required", file=sys.stderr)
        parser.print_help()
        sys.exit(1)
    
    if not args.from_file:
        print("Error: --from-file is required", file=sys.stderr)
        parser.print_help()
        sys.exit(1)
    
    try:
        # Parse variables if provided
        variables = None
        if args.variables:
            import json
            try:
                variables = json.loads(args.variables)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON in --variables: {e}", file=sys.stderr)
                sys.exit(1)
        
        # Convert the workout
        result = convert_workout(
            from_format=args.from_format,
            from_file=args.from_file,
            to_format=args.to_format,
            variables=variables
        )
        
        # Output result
        if args.output_file:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"Converted workout saved to: {args.output_file}")
        else:
            print(result)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
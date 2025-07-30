import json
import tempfile
from pathlib import Path

from structured_workouts.cli import ParserRegistry, convert_workout


class TestCLI:
    def setup_method(self):
        self.registry = ParserRegistry()
    
    def test_parser_registry(self):
        """Test that the parser registry works correctly."""
        formats = self.registry.get_available_formats()
        assert "intervals-icu-text" in formats
        
        parser = self.registry.get_parser("intervals-icu-text")
        assert parser.format_name == "Intervals.icu Text Format"
        assert parser.supports_import()
        assert parser.supports_export()
    
    def test_convert_workout(self):
        """Test basic workout conversion functionality."""
        # Create a temporary intervals.icu text file
        intervals_text = """Warmup
- 10m 50%

Main set 2x
- 5m 100%
- 2m 40%

Cooldown
- 10m 60%"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(intervals_text)
            temp_file = Path(f.name)
        
        try:
            # Test conversion to SWF
            result = convert_workout(
                from_format="intervals-icu-text",
                from_file=temp_file,
                to_format="swf"
            )
            
            # Verify it's valid JSON and contains expected structure
            workout_data = json.loads(result)
            assert "title" in workout_data
            assert "content" in workout_data
            assert len(workout_data["content"]) == 3  # Warmup, Main set, Cooldown
            
            # Test round-trip conversion
            result_text = convert_workout(
                from_format="intervals-icu-text",
                from_file=temp_file,
                to_format="intervals-icu-text"
            )
            
            # Should contain the key elements
            assert "Warmup" in result_text
            assert "- 10m 50%" in result_text
            assert "Main set 2x" in result_text
            assert "- 5m 100%" in result_text
            assert "Cooldown" in result_text
            
        finally:
            # Clean up
            temp_file.unlink()
    
    def test_format_detection(self):
        """Test format detection from file extensions."""
        # Test .txt detection
        txt_file = Path("workout.txt")
        detected = self.registry.detect_format_from_extension(txt_file)
        assert detected == "intervals-icu-text"
        
        # Test unknown extension
        unknown_file = Path("workout.xyz")
        detected = self.registry.detect_format_from_extension(unknown_file)
        assert detected is None
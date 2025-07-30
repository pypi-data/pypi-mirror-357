from structured_workouts.parsers import IntervalsICUTextParser, IntervalsICUAPIParser
from structured_workouts.schema import Workout
from structured_workouts.base import (
    Interval, Repeat, Section, Instruction, 
    ConstantValue, RangeValue, Value, Reference,
    VolumeQuantity, IntensityQuantity, RepeatQuantity
)


class TestIntervalsICUTextParser:
    def setup_method(self):
        self.parser = IntervalsICUTextParser()
    
    def test_parser_properties(self):
        assert self.parser.format_name == "Intervals.icu Text Format"
        assert '.txt' in self.parser.file_extensions
        assert self.parser.supports_import()  # Now supports both import and export
        assert self.parser.supports_export()
    
    def test_simple_interval_formatting(self):
        interval = Interval(
            volume=ConstantValue(
                value=Value(reference=Reference.absolute, value=10*60), 
                quantity=VolumeQuantity.duration
            ),
            intensity=ConstantValue(
                value=Value(reference=Reference.parameter, value=0.6, parameter="threshold"),
                quantity=IntensityQuantity.power)
        )
        workout = Workout(content=[interval])
        
        result = self.parser.to_format(workout)
        assert "- 10m 60%" in result
    
    def test_repeat_formatting(self):
        # In intervals.icu format, repeats are within sections
        repeat = Repeat(
            type="repeat",
            count=ConstantValue(value=Value(reference=Reference.absolute, value=5), quantity=RepeatQuantity.NUMBER),
            content=[
                Interval(
                    volume=ConstantValue(value=Value(reference=Reference.absolute, value=4*60), quantity=VolumeQuantity.duration),
                    intensity=ConstantValue(value=Value(reference=Reference.parameter, value=1.0, parameter="threshold"), quantity=IntensityQuantity.power)
                ),
                Interval(
                    volume=ConstantValue(value=Value(reference=Reference.absolute, value=1*60), quantity=VolumeQuantity.duration),
                    intensity=ConstantValue(value=Value(reference=Reference.parameter, value=0.4, parameter="threshold"), quantity=IntensityQuantity.power)
                )
            ]
        )
        section = Section(name="Main set", content=[repeat])
        workout = Workout(content=[section])
        
        result = self.parser.to_format(workout)
        assert "Main set 5x" in result
        assert "- 4m 100%" in result
        assert "- 1m 40%" in result

        workout = Workout(content=[repeat])

        result = self.parser.to_format(workout)
        assert "5x" in result
        assert "- 4m 100%" in result
        assert "- 1m 40%" in result
    
    def test_range_intensity_formatting(self):
        interval = Interval(
            volume=ConstantValue(value=Value(reference=Reference.absolute, value=20*60), quantity=VolumeQuantity.duration),
            intensity=RangeValue(
                min=Value(reference=Reference.absolute, value=250),
                max=Value(reference=Reference.absolute, value=350),
                quantity=IntensityQuantity.power)
        )
        workout = Workout(content=[interval])
        
        result = self.parser.to_format(workout)
        assert "- 20m 250-350W" in result
    
    def test_workout_with_title_and_description(self):
        # Intervals.icu format doesn't include title/description in output
        workout = Workout(
            description="This is a test workout",
            content=[
                Interval(
                    volume=ConstantValue(value=Value(reference=Reference.absolute, value=10*60), quantity=VolumeQuantity.duration),
                    intensity=ConstantValue(value=Value(reference=Reference.absolute, value=200), quantity=IntensityQuantity.power)
                )
            ]
        )
        
        result = self.parser.to_format(workout)
        # Title and description are not included in intervals.icu format
        assert "Test Workout" not in result
        assert "# This is a test workout" not in result
        assert "- 10m 200W" in result
    
    def test_section_formatting(self):
        section = Section(
            name="Warm-up",
            content=[
                Interval(
                    volume=ConstantValue(value=Value(reference=Reference.absolute, value=5*60), quantity=VolumeQuantity.duration),
                    intensity=ConstantValue(value=Value(reference=Reference.parameter, value=0.5, parameter="threshold"), quantity=IntensityQuantity.power)
                )
            ]
        )
        workout = Workout(content=[section])
        
        result = self.parser.to_format(workout)
        assert "Warm-up" in result  # Section name without special formatting
        assert "- 5m 50%" in result
    
    def test_instruction_formatting(self):
        instruction = Instruction(text="Keep cadence above 90 RPM")
        workout = Workout(content=[instruction])
        
        result = self.parser.to_format(workout)
        assert "Keep cadence above 90 RPM" in result
    
    def test_distance_volume_formatting(self):
        interval = Interval(
            volume=ConstantValue(value=Value(reference=Reference.absolute, value=5), quantity=VolumeQuantity.distance),
            intensity=ConstantValue(value=Value(reference=Reference.absolute, value=275), quantity=IntensityQuantity.power)
        )
        workout = Workout(title="Test", content=[interval])
        
        result = self.parser.to_format(workout)
        assert "5km 275W" in result
    
    def test_import_simple_intervals(self):
        text = """Warmup
- 20m 60%

Cooldown  
- 10m 50%"""
        
        workout = self.parser.from_format(text)
        assert len(workout.content) == 2
        
        # Check warmup section
        warmup = workout.content[0]
        assert isinstance(warmup, Section)
        assert warmup.name == "Warmup"
        assert len(warmup.content) == 1
        
        interval = warmup.content[0]
        assert isinstance(interval, Interval)
        assert interval.volume.value.value == 20*60  # 20 minutes = 1200 seconds
        assert interval.intensity.value.reference == Reference.parameter and interval.intensity.value.parameter == "threshold"
        assert interval.intensity.value.value == 0.6
    
    def test_import_with_repeat(self):
        text = """Main set 3x
- 5m 100%
- 2m 40%"""
        
        workout = self.parser.from_format(text)
        assert len(workout.content) == 1
        
        section = workout.content[0]
        assert isinstance(section, Section)
        assert section.name == "Main set"
        assert len(section.content) == 1
        
        repeat = section.content[0]
        assert isinstance(repeat, Repeat)
        assert repeat.count.value.value == 3
        assert len(repeat.content) == 2
    
    def test_import_with_description(self):
        text = """Main set 2x
- 4m 100%, power is less important than getting the torque
- 5m recovery at 40%"""
        
        workout = self.parser.from_format(text)
        section = workout.content[0]
        repeat = section.content[0]
        
        # First item should be instruction (has description)
        assert isinstance(repeat.content[0], Instruction)
        assert "power is less important" in repeat.content[0].text
        
        # Second item should be parsed as interval
        assert isinstance(repeat.content[1], Interval)
        assert repeat.content[1].volume.value.value == 5*60  # 5 minutes = 300 seconds
        assert repeat.content[1].intensity.value.value == 0.4
    
    def test_round_trip(self):
        """Test that parsing and formatting round trips correctly."""
        original_text = """Warmup
- 20m 60%

Main set 6x
- 4m 100%
- 5m recovery at 40%

Cooldown
- 20m 60%"""
        
        workout = self.parser.from_format(original_text)
        converted_text = self.parser.to_format(workout)
        
        # Parse again to check structure is preserved
        workout2 = self.parser.from_format(converted_text)
        
        assert len(workout.content) == len(workout2.content)
        assert workout.content[0].name == workout2.content[0].name


class TestIntervalsICUAPIParser:
    def setup_method(self):
        self.parser = IntervalsICUAPIParser()
    
    def test_parser_properties(self):
        assert self.parser.format_name == "Intervals.icu API JSON"
        assert '.json' in self.parser.file_extensions
        assert self.parser.supports_import()
        assert self.parser.supports_export()
    
    def test_basic_api_import(self):
        api_json = '''
        {
            "id": 12345,
            "name": "Test Workout",
            "description": "Warmup\\n- 10m 50%\\n\\nMain\\n- 20m 80%",
            "athlete_id": "abc123",
            "target": "POWER"
        }
        '''
        
        workout = self.parser.from_format(api_json)
        assert workout.title == "Test Workout"
        assert len(workout.content) == 2  # Warmup and Main sections
        
        warmup = workout.content[0]
        assert warmup.name == "Warmup"
        assert len(warmup.content) == 1
        
        main = workout.content[1]
        assert main.name == "Main"
    
    def test_api_import_with_complex_workout(self):
        api_json = '''
        {
            "name": "Interval Session",
            "description": "Main set 3x\\n- 5m 100%\\n- 2m 40%\\n\\nCooldown\\n- 15m 60%",
            "indoor": true,
            "target": "POWER"
        }
        '''
        
        workout = self.parser.from_format(api_json)
        assert workout.title == "Interval Session"
        assert len(workout.content) == 2
        
        # Check repeat structure in main set
        main_set = workout.content[0]
        assert main_set.name == "Main set"
        assert len(main_set.content) == 1
        
        repeat = main_set.content[0]
        assert isinstance(repeat, Repeat)
        assert repeat.count.value.value == 3
    
    def test_api_import_empty_description(self):
        api_json = '''
        {
            "name": "Empty Workout",
            "description": "",
            "target": "HR"
        }
        '''
        
        workout = self.parser.from_format(api_json)
        assert workout.title == "Empty Workout"
        assert len(workout.content) == 0
    
    def test_api_import_missing_description(self):
        api_json = '''
        {
            "name": "No Description Workout",
            "athlete_id": "test123"
        }
        '''
        
        workout = self.parser.from_format(api_json)
        assert workout.title == "No Description Workout"
        assert len(workout.content) == 0
    
    def test_api_export_basic(self):
        workout = Workout(
            title="Export Test",
            content=[
                Interval(
                    volume=ConstantValue(value=Value(reference=Reference.absolute, value=30*60), quantity=VolumeQuantity.duration),
                    intensity=ConstantValue(value=Value(reference=Reference.parameter, value=0.7, parameter="threshold"), quantity=IntensityQuantity.power)
                )
            ]
        )
        
        result = self.parser.to_format(workout)
        
        # Parse back to verify structure
        import json
        api_data = json.loads(result)
        
        assert api_data["name"] == "Export Test"
        assert "- 30m 70%" in api_data["description"]
        assert api_data["type"] == "Workout"
        assert api_data["hide_from_athlete"] is False
    
    def test_api_export_with_options(self):
        workout = Workout(
            title="Test with Options",
            content=[
                Interval(
                    volume=ConstantValue(value=Value(reference=Reference.absolute, value=10*60), quantity=VolumeQuantity.duration),
                    intensity=ConstantValue(value=Value(reference=Reference.absolute, value=250), quantity=IntensityQuantity.power)
                )
            ]
        )
        
        result = self.parser.to_format(
            workout,
            athlete_id="athlete123",
            workout_id=456,
            folder_id=789,
            target="POWER",
            indoor=True
        )
        
        import json
        api_data = json.loads(result)
        
        assert api_data["athlete_id"] == "athlete123"
        assert api_data["id"] == 456
        assert api_data["folder_id"] == 789
        assert api_data["target"] == "POWER"
        assert api_data["indoor"] is True
    
    def test_api_export_with_workout_description(self):
        workout = Workout(
            title="Workout with Description",
            description="This workout focuses on threshold power",
            content=[
                Interval(
                    volume=ConstantValue(value=Value(reference=Reference.absolute, value=20*60), quantity=VolumeQuantity.duration),
                    intensity=ConstantValue(value=Value(reference=Reference.parameter, value=1.0, parameter="threshold"), quantity=IntensityQuantity.power)
                )
            ]
        )
        
        result = self.parser.to_format(workout)
        
        import json
        api_data = json.loads(result)
        
        # Should include both generated description and workout description
        assert "- 20m 100%" in api_data["description"]
        assert "This workout focuses on threshold power" in api_data["description"]
    
    def test_invalid_json_error(self):
        invalid_json = '{"name": "Test", "description": invalid}'
        
        try:
            self.parser.from_format(invalid_json)
            assert False, "Should have raised ParseError"
        except Exception as e:
            assert "Invalid JSON" in str(e)
    
    def test_round_trip_conversion(self):
        original_api_json = '''
        {
            "name": "Round Trip Test",
            "description": "Warmup\\n- 15m 55%\\n\\nMain set 2x\\n- 8m 95%\\n- 3m 45%",
            "target": "POWER",
            "indoor": false
        }
        '''
        
        # Import from API JSON
        workout = self.parser.from_format(original_api_json)
        
        # Export back to API JSON
        exported_json = self.parser.to_format(workout, target="POWER", indoor=False)
        
        # Import again to verify structure is preserved
        workout2 = self.parser.from_format(exported_json)
        
        assert workout.title == workout2.title
        assert len(workout.content) == len(workout2.content)
        
        # Verify the repeat structure is preserved
        main_set = workout2.content[1]
        assert main_set.name == "Main set"
        repeat = main_set.content[0]
        assert isinstance(repeat, Repeat)
        assert repeat.count.value.value == 2
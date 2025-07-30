"""
Upload a workout to Intervals.icu API for the current date.

This script demonstrates how to create a simple workout using the structured-workouts
library and upload it to Intervals.icu via their API.

Usage:
    python upload_to_intervals_icu.py

Environment Variables Required:
    INTERVALS_ICU_API_KEY: Your Intervals.icu API key
    INTERVALS_ICU_ATHLETE_ID: Your athlete ID (or use 'i' for current user)
"""

# /// script
# dependencies = [
#   "httpx>=0.25.0",
#   "python-dotenv>=1.0.0",
#   "pydantic>=2.0.0",
# ]
# ///

import os
import sys
from datetime import date, datetime
from pathlib import Path

# Add the src directory to Python path to import structured_workouts
script_dir = Path(__file__).parent
src_dir = script_dir.parent / "src"
sys.path.insert(0, str(src_dir))

import httpx

from structured_workouts import Workout
from structured_workouts.base import (
    Interval, Section, ConstantValue, Value, Reference,
    VolumeQuantity, IntensityQuantity
)
from structured_workouts.parsers import IntervalsICUAPIParser


def load_environment():
    """Load environment variables from .env file if present."""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)


def get_api_credentials():
    """Get API credentials from environment variables."""
    api_key = os.getenv("INTERVALS_ICU_API_KEY")
    athlete_id = os.getenv("INTERVALS_ICU_ATHLETE_ID", "i")  # 'i' means current user
    
    if not api_key:
        print("Error: INTERVALS_ICU_API_KEY environment variable not set")
        print("Please set your API key:")
        print("  export INTERVALS_ICU_API_KEY='your_api_key_here'")
        print("\nYou can get your API key from:")
        print("  https://intervals.icu/settings")
        return None, None
    
    return api_key, athlete_id


def create_sample_workout():
    """Create a sample workout using the structured-workouts library."""
    
    # Create a threshold workout
    workout = Workout(
        title="Structured Workout Upload Test",
        description="Automatically uploaded via structured-workouts library",
        content=[
            Section(
                name="Warmup",
                content=[
                    Interval(
                        volume=ConstantValue(
                            value=Value(reference=Reference.absolute, value=15*60),
                            quantity=VolumeQuantity.duration
                        ),
                        intensity=ConstantValue(
                            value=Value(reference=Reference.parameter, value=0.55, parameter="threshold"),
                            quantity=IntensityQuantity.power
                        )
                    )
                ]
            ),
            Section(
                name="Main Set",
                content=[
                    Interval(
                        volume=ConstantValue(
                            value=Value(reference=Reference.absolute, value=20*60),
                            quantity=VolumeQuantity.duration
                        ),
                        intensity=ConstantValue(
                            value=Value(reference=Reference.parameter, value=0.95, parameter="threshold"),
                            quantity=IntensityQuantity.power
                        )
                    ),
                    Interval(
                        volume=ConstantValue(
                            value=Value(reference=Reference.absolute, value=5*60),
                            quantity=VolumeQuantity.duration
                        ),
                        intensity=ConstantValue(
                            value=Value(reference=Reference.parameter, value=0.60, parameter="threshold"),
                            quantity=IntensityQuantity.power
                        )
                    ),
                    Interval(
                        volume=ConstantValue(
                            value=Value(reference=Reference.absolute, value=15*60),
                            quantity=VolumeQuantity.duration
                        ),
                        intensity=ConstantValue(
                            value=Value(reference=Reference.parameter, value=1.00, parameter="threshold"),
                            quantity=IntensityQuantity.power
                        )
                    ),
                    Interval(
                        volume=ConstantValue(
                            value=Value(reference=Reference.absolute, value=5*60),
                            quantity=VolumeQuantity.duration
                        ),
                        intensity=ConstantValue(
                            value=Value(reference=Reference.parameter, value=0.60, parameter="threshold"),
                            quantity=IntensityQuantity.power
                        )
                    )
                ]
            ),
            Section(
                name="Cooldown",
                content=[
                    Interval(
                        volume=ConstantValue(
                            value=Value(reference=Reference.absolute, value=10*60),
                            quantity=VolumeQuantity.duration
                        ),
                        intensity=ConstantValue(
                            value=Value(reference=Reference.parameter, value=0.50, parameter="threshold"),
                            quantity=IntensityQuantity.power
                        )
                    )
                ]
            )
        ]
    )
    
    return workout


def convert_workout_to_api_format(workout, athlete_id):
    """Convert the workout to Intervals.icu API format."""
    parser = IntervalsICUAPIParser()
    
    # Convert to API JSON format with metadata
    api_json_str = parser.to_format(
        workout,
        athlete_id=athlete_id,
        target="POWER",
        indoor=True,
        # Note: Don't set workout_id for new workouts
    )
    
    # Parse back to dict for API call
    import json
    return json.loads(api_json_str)


def upload_workout_to_intervals_icu(workout_data, api_key, athlete_id):
    """Upload the workout to Intervals.icu API."""
    
    # API endpoint for creating events (workouts)
    url = f"https://intervals.icu/api/v1/athlete/{athlete_id}/events"
    
    today = datetime.combine(date.today(), datetime.min.time())
    workout_data["start_date_local"] = today.isoformat()
    workout_data["category"] = "WORKOUT"
    workout_data["type"] = "Ride"
    
    print("Uploading workout to Intervals.icu...")
    print(f"Athlete ID: {athlete_id}")
    print(f"Date: {today}")
    print(f"Workout: {workout_data['name']}")
    
    try:
        # Use httpx with proper basic auth (username=API_KEY, password=api_key)
        with httpx.Client() as client:
            response = client.post(
                url,
                json=workout_data,
                auth=("API_KEY", api_key),
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            result = response.json()
            print("✅ Workout uploaded successfully!")
            print(f"Event ID: {result.get('id')}")
            print(f"URL: https://intervals.icu/calendar#{today}")
            
            return result
        
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"Response content: {e.response.text}")
        if e.response.status_code == 401:
            print("Check your API key and athlete ID")
        elif e.response.status_code == 400:
            print("Bad request - check workout data format")
        return None
        
    except httpx.RequestError as e:
        print(f"❌ Request Error: {e}")
        return None


def main():
    """Main function to create and upload a workout."""
    print("🚴 Intervals.icu Workout Upload Tool")
    print("=====================================\n")
    
    # Load environment variables
    load_environment()
    
    # Get API credentials
    api_key, athlete_id = get_api_credentials()
    if not api_key:
        return 1
    
    print(f"Using athlete ID: {athlete_id}")
    
    # Create sample workout
    print("\n📝 Creating sample workout...")
    workout = create_sample_workout()
    
    # Show workout structure
    print(f"Workout: {workout.title}")
    print(f"Sections: {len(workout.content)}")
    for i, section in enumerate(workout.content, 1):
        if hasattr(section, 'name'):
            print(f"  {i}. {section.name} ({len(section.content)} intervals)")
    
    # Convert to API format
    print("\n🔄 Converting to Intervals.icu API format...")
    workout_data = convert_workout_to_api_format(workout, athlete_id)
    
    # Show the description that will be uploaded
    print("\nWorkout description:")
    print(workout_data['description'])
    
    # Confirm upload
    response = input(f"\n📤 Upload this workout to Intervals.icu for {date.today()}? (y/N): ")
    if response.lower() not in ['y', 'yes']:
        print("Upload cancelled.")
        return 0
    
    # Upload to Intervals.icu
    result = upload_workout_to_intervals_icu(workout_data, api_key, athlete_id)
    
    if result:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
# Scripts Directory

This directory contains utility scripts that demonstrate how to use the structured-workouts library in real-world scenarios.

## upload_to_intervals_icu.py

Demonstrates how to create a workout programmatically and upload it to Intervals.icu via their API.

### Features

- Creates a sample threshold-based workout with warmup, main set, and cooldown
- Converts the workout to Intervals.icu API format using `IntervalsICUAPIParser`
- Uploads the workout to your Intervals.icu calendar for today's date
- Uses inline dependency management compatible with `uv run`

### Setup

1. Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```

2. Get your API key from https://intervals.icu/settings/developer

3. Edit `.env`:
   ```bash
   INTERVALS_ICU_API_KEY=your_api_key_here
   INTERVALS_ICU_ATHLETE_ID=i
   ```

### Usage

With uv (recommended - automatically manages dependencies):
```bash
uv run scripts/upload_to_intervals_icu.py
```

Or with manual dependency installation:
```bash
pip install httpx python-dotenv pydantic
python scripts/upload_to_intervals_icu.py
```

### Sample Workout

The script creates a 70-minute threshold workout:

```
Warmup
- 15m 55%

Main Set  
- 20m 95%
- 5m 60%
- 15m 100%
- 5m 60%

Cooldown
- 10m 50%
```

All percentages are relative to threshold power (FTP).
# Structured Workout Format (SWF)

This document describes a JSON format for representing structured workouts. The format supports various types of intervals, repeats, sections, and instructions, making it suitable for describing both simple and complex workouts.

The goal of `SWF` is to be simple and easy to understand, while also being flexible and powerful enough to represent complex workouts.
`SWF` should be also able to serve as an intermediate format for converting to (and from) other formats.

The `SWF` format is accompanied by a Python implementation that serves as an official reference implementation, but note that `SWF` is in no way intended to be limited or tied to Python.

## Simple Example

Here's the most basic example of a workout with a single interval in the Structured Workout Format:

```json
{
  "title": "Simple Run",
  "description": "A 10-minute run at constant pace",
  "content": [
    {
      "type": "interval",
      "volume": {
        "type": "constant",
        "quantity": "duration",
        "value": {
          "reference": "absolute",
          "value": 600
        }
      },
      "intensity": {
        "type": "constant",
        "quantity": "speed",
        "value": {
          "reference": "absolute",
          "value": 3.33
        }
      }
    }
  ]
}
```

## Quantities and Units

The format supports the following quantities with their respective units:

### Volume Quantities
- `duration`: Time in seconds
- `distance`: Distance in meters

### Intensity Quantities
- `speed`: Speed in meters per second (m/s)
- `power`: Power in watts (W)

## Value Specifications

Value specifications are used to specify the volume and intensity of intervals or the number of repeats in a repeat. The new schema uses a unified approach with three intensity types and three reference types.

```json
{
  "title": null,
  "description": null,
  "content": [
    {
      "type": "interval",
      "volume": <--- THIS IS WHERE THE VALUE SPECIFICATION FOR VOLUME GOES,
      "intensity": <--- THIS IS WHERE THE VALUE SPECIFICATION FOR INTENSITY GOES
    }
  ]
}
```

There are three ways to specify values for quantities: **constant**, **range**, and **ramp**.

### Intensity Types

#### 1. Constant Value Specification

A single specific value:

```json
{
  "type": "constant",
  "quantity": "speed",
  "value": {
    "reference": "absolute",
    "value": 3.33
  }
}
```

#### 2. Range Value Specification

A range between min and max values. Both `min` and `max` are optional - you can specify just one to create an open-ended range:

```json
{
  "type": "range",
  "quantity": "power",
  "min": {
    "reference": "absolute",
    "value": 200
  },
  "max": {
    "reference": "absolute",
    "value": 250
  }
}
```

Open-ended range example:
```json
{
  "type": "range",
  "quantity": "speed",
  "min": {
    "reference": "absolute",
    "value": 2.5
  }
}
```

#### 3. Ramp Value Specification

A linear progression from start to end. Both `start` and `end` are required:

```json
{
  "type": "ramp",
  "quantity": "speed",
  "start": {
    "reference": "absolute",
    "value": 2.5
  },
  "end": {
    "reference": "absolute",
    "value": 3.5
  }
}
```

### Reference Types

Each value uses a `reference` field to specify how the intensity should be interpreted:

#### 1. Absolute Reference

Direct, literal values:

```json
{
  "reference": "absolute",
  "value": 250
}
```

#### 2. Parameter Reference

Fractions of named variables (e.g., percentages of FTP):

```json
{
  "reference": "parameter",
  "value": 0.75,
  "parameter": "FTP"
}
```

#### 3. Time-to-Exhaustion (TTE) Reference

Intensities based on how long you can sustain them:

```json
{
  "reference": "tte",
  "value": 300
}
```

This represents "the power (or speed) you can hold for 300 seconds".

### Complete Examples

#### Parameter-based intensity (75% of FTP):
```json
{
  "type": "constant",
  "quantity": "power",
  "value": {
    "reference": "parameter",
    "value": 0.75,
    "parameter": "FTP"
  }
}
```

#### TTE-based intensity:
```json
{
  "type": "constant",
  "quantity": "power",
  "value": {
    "reference": "tte",
    "value": 600
  }
}
```

#### Range with mixed references:
```json
{
  "type": "range",
  "quantity": "power",
  "min": {
    "reference": "tte",
    "value": 1200
  },
  "max": {
    "reference": "parameter",
    "value": 0.85,
    "parameter": "FTP"
  }
}
```

#### Ramp from absolute to parameter:
```json
{
  "type": "ramp",
  "quantity": "power",
  "start": {
    "reference": "absolute",
    "value": 150
  },
  "end": {
    "reference": "parameter",
    "value": 0.9,
    "parameter": "FTP"
  }
}
```

## Intervals

An interval combines volume and intensity, both specified using value specifications:

```json
{
  "type": "interval",
  "volume": {
    "type": "constant",
    "quantity": "duration",
    "value": {
      "reference": "absolute",
      "value": 300
    }
  },
  "intensity": {
    "type": "constant",
    "quantity": "speed",
    "value": {
      "reference": "absolute",
      "value": 3.33
    }
  }
}
```

## Sections

Sections help organize workouts into logical parts. The names "warm up", "main set", and "cool down" have special meaning:

```json
{
  "type": "section",
  "name": "warm up",
  "content": [
    {
      "type": "interval",
      "volume": {
        "type": "constant",
        "quantity": "duration",
        "value": {
          "reference": "absolute",
          "value": 600
        }
      },
      "intensity": {
        "type": "constant",
        "quantity": "speed",
        "value": {
          "reference": "absolute",
          "value": 2.5
        }
      }
    }
  ]
}
```

Sections can be nested within other sections or repeats.

## Repeats

Repeats allow you to specify recurring patterns. They can be nested within sections or other repeats. The repeat count can be a constant number, a range, or a parameter reference:

```json
{
  "type": "repeat",
  "count": {
    "type": "constant",
    "quantity": "number",
    "value": {
      "reference": "absolute",
      "value": 4
    }
  },
  "content": [
    {
      "type": "interval",
      "volume": {
        "type": "constant",
        "quantity": "duration",
        "value": {
          "reference": "absolute",
          "value": 60
        }
      },
      "intensity": {
        "type": "constant",
        "quantity": "speed",
        "value": {
          "reference": "absolute",
          "value": 4.0
        }
      }
    }
  ]
}
```

Example with a range for repeat count:
```json
{
  "type": "repeat",
  "count": {
    "type": "range",
    "quantity": "number",
    "min": {
      "reference": "absolute",
      "value": 3
    },
    "max": {
      "reference": "absolute",
      "value": 5
    }
  },
  "content": [
    // ... intervals ...
  ]
}
```

Example with a parameter for repeat count:
```json
{
  "type": "repeat",
  "count": {
    "type": "constant",
    "quantity": "number",
    "value": {
      "reference": "parameter",
      "value": 1.0,
      "parameter": "INTERVAL_COUNT"
    }
  },
  "content": [
    // ... intervals ...
  ]
}
```

## Instructions

Instructions provide text guidance within the workout:

```json
{
  "type": "instruction",
  "text": "Focus on maintaining good form"
}
```

## Complete Example

Here's a simple complete workout with sections and repeats:

```json
{
  "title": "Basic Interval Session",
  "description": "A simple workout with warm up, intervals, and cool down",
  "content": [
    {
      "type": "section",
      "name": "warm up",
      "content": [
        {
          "type": "interval",
          "volume": {
            "type": "constant",
            "quantity": "duration",
            "value": {
              "reference": "absolute",
              "value": 600
            }
          },
          "intensity": {
            "type": "constant",
            "quantity": "speed",
            "value": {
              "reference": "absolute",
              "value": 2.5
            }
          }
        }
      ]
    },
    {
      "type": "section",
      "name": "main set",
      "content": [
        {
          "type": "repeat",
          "count": {
            "type": "constant",
            "quantity": "number",
            "value": {
              "reference": "absolute",
              "value": 3
            }
          },
          "content": [
            {
              "type": "interval",
              "volume": {
                "type": "constant",
                "quantity": "duration",
                "value": {
                  "reference": "absolute",
                  "value": 180
                }
              },
              "intensity": {
                "type": "constant",
                "quantity": "speed",
                "value": {
                  "reference": "absolute",
                  "value": 3.5
                }
              }
            },
            {
              "type": "interval",
              "volume": {
                "type": "constant",
                "quantity": "duration",
                "value": {
                  "reference": "absolute",
                  "value": 60
                }
              },
              "intensity": {
                "type": "constant",
                "quantity": "speed",
                "value": {
                  "reference": "absolute",
                  "value": 0
                }
              }
            },
            {
              "type": "instruction",
              "text": "It is allowed to walk between intervals"
            }
          ]
        }
      ]
    },
    {
      "type": "section",
      "name": "cool down",
      "content": [
        {
          "type": "interval",
          "volume": {
            "type": "constant",
            "quantity": "duration",
            "value": {
              "reference": "absolute",
              "value": 300
            }
          },
          "intensity": {
            "type": "constant",
            "quantity": "speed",
            "value": {
              "reference": "absolute",
              "value": 2.0
            }
          }
        }
      ]
    }
  ]
}
```
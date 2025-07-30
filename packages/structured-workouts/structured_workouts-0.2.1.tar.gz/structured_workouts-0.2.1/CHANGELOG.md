# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.2.1] - 2025-06-24

### Fixed
- **Parser Bug**: Fixed a bug in the intervals.icu text parser that caused repeats to be formatted incorrectly.


## [0.2.0] - 2025-06-24

### Added
- **Time-to-Exhaustion (TTE) Reference Type**: New intensity specification method allowing workouts to specify intensities based on time-to-exhaustion (e.g., "power you can hold for 300 seconds")
- **Enhanced Reference System**: Unified value specification with three reference types: `absolute`, `parameter`, and `tte`

### Changed
- **BREAKING: Schema Redesign**: Complete overhaul of value specifications to use reference-based approach
  - Renamed `"fixed"` type to `"constant"` for clarity
  - Replaced separate `variable` and `fraction` fields with unified `Value` objects containing `reference`, `value`, and optional `parameter` fields
  - Simplified field names: `min_value`/`max_value` → `min`/`max`, `start_value`/`end_value` → `start`/`end`
- **BREAKING: API Changes**: 
  - `FixedValue` class renamed to `ConstantValue`
  - All value specifications now use nested `Value` objects with explicit reference types
  - Updated validation logic to work with new schema structure
- **Documentation**: Complete rewrite of README.md and README_SWF.md to reflect new schema
- **Examples**: Updated all code examples and test data to use new reference-based format

### Migration Guide
```python
# Old format
FixedValue(variable="FTP", fraction=0.75, quantity=IntensityQuantity.power)

# New format  
ConstantValue(
    value=Value(reference=Reference.parameter, value=0.75, parameter="FTP"),
    quantity=IntensityQuantity.power
)
```



## [0.1.0] - 2025-06-10

### Added

- Initial release of the Structured Workout Format (SWF) library and schema
- **Note**: This is the first public release. The schema and library API should not be considered stable and may undergo breaking changes in future releases. Users are strongly advised to pin their dependency versions and test thoroughly before upgrading.
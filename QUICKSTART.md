# Quick Start Guide

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

Or install as a package:
```bash
pip install -e .
```

## Running Examples

### Example 1: Basic Usage
```bash
python -m electrotrack.main
```

### Example 2: Detailed Examples
```bash
python examples/example_usage.py
```

### Example 3: Validation Tests
```bash
python tests/validation.py
```

## Expected Output

When you run the examples, you should see output like:

```
ElectroTrack - AI-Powered Hydration Monitoring System
============================================================

--- Example 1: High-Intensity 10K Run ---

Recommendation:
Recommended: 0.60 L of medium-sodium electrolyte drink within 30 minutes post-workout.
Reason: Significant weight loss (1.20 kg) High temperature (85.0°F) High intensity (avg HR: 175 bpm) Electrolyte replacement needed due to sodium loss.

Future suggestions:
- Consider pre-hydration before workouts in hot conditions (>85°F)
- For high-intensity workouts, consider carrying hydration during exercise
```

## Troubleshooting

### ModuleNotFoundError
If you see `ModuleNotFoundError`, install dependencies:
```bash
pip install -r requirements.txt
```

### Import Errors
Make sure you're running from the project root directory:
```bash
cd /path/to/python
python -m electrotrack.main
```

### Python Version
Requires Python 3.8 or higher:
```bash
python3 --version
```

## Next Steps

1. **Register Athletes**: Create athlete profiles with physiological data
2. **Collect Data**: Record workouts with metrics and environmental conditions
3. **Train Model**: After collecting 10+ workouts, train the ML model
4. **Validate**: Use the validation framework to test predictions
5. **Deploy**: Integrate into your athlete monitoring system

See README.md for detailed documentation.


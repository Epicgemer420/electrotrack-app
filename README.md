# ElectroTrack

AI-Powered Hydration Monitoring System for Track and Field Athletes

## Overview

ElectroTrack is an intelligent hydration monitoring system that integrates biometric, environmental, and performance data to estimate electrolyte loss and provide personalized hydration guidance for track and field athletes. The system addresses performance and safety issues caused by misjudged hydration through machine learning and real-time data processing.

## Features

- **Personalized Recommendations**: AI-powered system adapts to individual athlete profiles and historical patterns
- **Real-Time Processing**: Monitor workouts in real-time with in-session feedback
- **Multi-Factor Analysis**: Considers heart rate, weight loss, environmental conditions, and workout intensity
- **Privacy-First**: Built-in encryption and anonymization for athlete data protection
- **ML-Powered**: Machine learning models learn from historical data to improve recommendations
- **Environmental Integration**: Automatic weather data integration for outdoor conditions

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from electrotrack.main import ElectroTrack
from electrotrack.models.athlete import AthleteProfile
from electrotrack.models.workout import WorkoutMetrics, EnvironmentalData, WorkoutType

# Initialize system
system = ElectroTrack()

# Register an athlete
profile = AthleteProfile(
    age=25,
    gender='M',
    weight_kg=70.0,
    height_cm=175.0,
    activity_level='competitive',
    baseline_heart_rate=60
)
athlete = system.register_athlete("athlete_001", profile)

# Define workout metrics
metrics = WorkoutMetrics(
    duration_minutes=45.0,
    average_heart_rate_bpm=175,
    pre_workout_weight_kg=70.0,
    post_workout_weight_kg=68.8,  # 1.2 kg loss
    fluid_intake_liters=1.5,
    workout_type=WorkoutType.DISTANCE,
    distance_km=10.0,
    intensity_level='high'
)

# Environmental conditions
environmental = EnvironmentalData(
    temperature_fahrenheit=85.0,
    humidity_percent=60.0,
    location="outdoor"
)

# Get recommendation
recommendation = system.get_recommendation(
    "athlete_001", metrics, environmental
)

print(recommendation)
```

### Example Output

```
Recommended: 0.60 L of medium-sodium electrolyte drink within 30 minutes post-workout.
Reason: Significant weight loss (1.20 kg) High temperature (85.0°F) High intensity (avg HR: 175 bpm) Electrolyte replacement needed due to sodium loss.

Future suggestions:
- Consider pre-hydration before workouts in hot conditions (>85°F)
- For high-intensity workouts, consider carrying hydration during exercise
```

## Examples

Run the example scripts to see the system in action:

```bash
# Run main examples
python -m electrotrack.main

# Run detailed examples
python examples/example_usage.py
```

## System Architecture

### Core Components

1. **Models** (`electrotrack/models/`): Data models for athletes, workouts, and recommendations
2. **ML Engine** (`electrotrack/ml/`): Machine learning models for hydration prediction
3. **Processor** (`electrotrack/processor/`): Real-time session processing
4. **API Integration** (`electrotrack/api/`): Weather and environmental data APIs
5. **Security** (`electrotrack/security/`): Encryption and anonymization utilities

### Data Flow

1. **Athlete Registration**: Athlete profile created with physiological data
2. **Workout Input**: Workout metrics and environmental conditions collected
3. **Feature Extraction**: ML model extracts features from athlete + workout data
4. **Prediction**: Model predicts hydration volume and electrolyte type needed
5. **Recommendation**: Personalized recommendation generated with reasoning
6. **Learning**: System learns from outcomes to improve future predictions

## Key Features

### Personalized Recommendations

The system considers:
- Individual athlete physiology (age, weight, gender, activity level)
- Historical workout patterns
- Real-time biometric data (heart rate, weight change)
- Environmental conditions (temperature, humidity)
- Workout characteristics (intensity, duration, type)

### Real-Time Processing

Monitor workouts in real-time:
```python
# Start session
session_id = system.start_workout_session(athlete_id, initial_metrics, environmental)

# Update during workout
recommendation = system.update_workout_session(session_id, updated_metrics)

# End session
workout, final_rec = system.end_workout_session(session_id, final_metrics)
```

### Machine Learning

Train the model on historical data:
```python
# After collecting workout data
training_metrics = system.train_model(min_workouts=10)
print(f"Training MAE: {training_metrics['volume_mae']}")

# Save model
system.save_model("models/hydration_model.pkl")
```

### Privacy & Security

- Data encryption for sensitive athlete information
- Anonymization for privacy-preserving analytics
- Secure storage patterns

## Configuration

### Weather API (Optional)

To use real-time weather data, set up OpenWeatherMap API:

```python
system = ElectroTrack(weather_api_key="your_api_key_here")
```

Get a free API key at: https://openweathermap.org/api

### Model Training

The system starts with rule-based recommendations. Train on historical data for ML-powered predictions:

```python
# After collecting 10+ workouts
system.train_model(min_workouts=10)
system.save_model("models/hydration_model.pkl")

# Load saved model
system = ElectroTrack(model_path="models/hydration_model.pkl")
```

## Validation Framework

Before deployment, validate the system:

1. **Controlled Trials**: Test with athletes in controlled conditions
2. **Data Collection**: Gather workout data and outcomes
3. **Model Training**: Train on collected data
4. **Performance Metrics**: Evaluate prediction accuracy
5. **Iterative Improvement**: Refine based on validation results

## Data Privacy

- Athlete IDs can be encrypted
- Anonymized data for analytics
- Secure data storage patterns
- Compliance-ready architecture

## Requirements

- Python 3.8+
- See `requirements.txt` for dependencies

## Constraints & Compliance

✅ **Python-based**: Implemented primarily in Python  
✅ **Open-source libraries**: Uses scikit-learn, numpy, pandas  
✅ **Real-time processing**: Near-real-time feedback during workouts  
✅ **Privacy protection**: Encryption and anonymization built-in  
✅ **Personalized**: Adapts to individual variability  
✅ **Validation-ready**: Framework for controlled athlete trials  

## License

This project is provided as-is for development and validation purposes.

## Contributing

This system is designed for validation through controlled athlete trials. Before production deployment:

1. Collect validation data from controlled trials
2. Train models on real athlete data
3. Validate prediction accuracy
4. Iterate based on feedback

## Support

For questions or issues, please refer to the code documentation or create an issue in the repository.


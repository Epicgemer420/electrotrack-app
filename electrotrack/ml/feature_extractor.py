"""Feature extraction for ML model"""

from typing import Dict, List
import numpy as np
from ..models.athlete import Athlete, AthleteProfile
from ..models.workout import Workout, WorkoutMetrics, EnvironmentalData


class FeatureExtractor:
    """Extract features from athlete and workout data for ML prediction"""
    
    @staticmethod
    def extract_features(
        athlete: Athlete,
        metrics: WorkoutMetrics,
        environmental: EnvironmentalData
    ) -> np.ndarray:
        """
        Extract feature vector for ML model
        
        Features:
        - Age, gender (encoded), weight, height
        - Workout duration, heart rate, intensity
        - Environmental conditions (temperature, humidity)
        - Historical patterns (if available)
        - Calculated metrics (weight loss, fluid loss)
        """
        features = []
        profile = athlete.profile
        
        # Athlete demographics
        features.append(profile.age)
        features.append(1.0 if profile.gender == 'M' else 0.0)  # Binary encoding
        features.append(profile.weight_kg)
        features.append(profile.height_cm / 100.0)  # Height in meters
        
        # Activity level encoding
        activity_encoding = {
            'recreational': 0.0,
            'competitive': 1.0,
            'elite': 2.0
        }
        features.append(activity_encoding.get(profile.activity_level, 1.0))
        
        # Personalized metrics (if available, otherwise use defaults)
        features.append(
            profile.sweat_rate_liter_per_hour or 1.0  # Default 1 L/hour
        )
        features.append(
            profile.sodium_loss_rate_mg_per_liter or 800.0  # Default 800 mg/L
        )
        features.append(
            profile.baseline_heart_rate or 60.0
        )
        
        # Workout metrics
        features.append(metrics.duration_minutes)
        features.append(metrics.average_heart_rate_bpm)
        features.append(metrics.max_heart_rate_bpm or metrics.average_heart_rate_bpm)
        features.append(metrics.calculate_weight_loss_kg())
        features.append(metrics.calculate_net_fluid_loss_liters())
        features.append(metrics.fluid_intake_liters)
        
        # Intensity encoding
        intensity_encoding = {
            'low': 0.0,
            'moderate': 1.0,
            'high': 2.0,
            'extreme': 3.0
        }
        features.append(intensity_encoding.get(metrics.intensity_level, 1.0))
        
        # Workout type encoding (one-hot like)
        workout_types = ['running', 'sprinting', 'distance', 'interval', 
                        'endurance', 'speed_work', 'cross_training']
        workout_encoding = [0.0] * len(workout_types)
        if metrics.workout_type.value in workout_types:
            idx = workout_types.index(metrics.workout_type.value)
            workout_encoding[idx] = 1.0
        features.extend(workout_encoding)
        
        # Distance (if available)
        features.append(metrics.distance_km or 0.0)
        
        # Environmental features
        features.append(environmental.temperature_fahrenheit)
        features.append(environmental.humidity_percent)
        features.append(environmental.wind_speed_mph or 0.0)
        
        # Calculated derived features
        # Heat index approximation (simplified)
        temp_c = (environmental.temperature_fahrenheit - 32) * 5/9
        heat_index = temp_c + (0.5 * (temp_c + 61.0) * ((environmental.humidity_percent - 68) / 100))
        features.append(heat_index)
        
        # Heart rate intensity (relative to baseline)
        hr_intensity = (metrics.average_heart_rate_bpm - 
                       (profile.baseline_heart_rate or 60)) / (profile.baseline_heart_rate or 60)
        features.append(hr_intensity)
        
        # Estimated sweat rate (based on conditions and intensity)
        estimated_sweat_rate = FeatureExtractor._estimate_sweat_rate(
            metrics, environmental, profile
        )
        features.append(estimated_sweat_rate)
        
        # Historical patterns (if available)
        if athlete.workout_history:
            recent_workouts = athlete.workout_history[-5:]  # Last 5 workouts
            avg_fluid_loss = np.mean([
                w.metrics.calculate_net_fluid_loss_liters() 
                for w in recent_workouts
            ])
            features.append(avg_fluid_loss)
        else:
            features.append(0.0)  # No history
        
        return np.array(features)
    
    @staticmethod
    def _estimate_sweat_rate(
        metrics: WorkoutMetrics,
        environmental: EnvironmentalData,
        profile: AthleteProfile
    ) -> float:
        """Estimate sweat rate based on conditions"""
        base_rate = profile.sweat_rate_liter_per_hour or 1.0
        
        # Temperature factor (higher temp = more sweat)
        temp_factor = 1.0 + (environmental.temperature_fahrenheit - 70) / 100
        
        # Humidity factor (higher humidity = less effective cooling = more sweat)
        humidity_factor = 1.0 + (environmental.humidity_percent - 50) / 200
        
        # Intensity factor
        intensity_factor = {
            'low': 0.7,
            'moderate': 1.0,
            'high': 1.5,
            'extreme': 2.0
        }.get(metrics.intensity_level, 1.0)
        
        return base_rate * temp_factor * humidity_factor * intensity_factor


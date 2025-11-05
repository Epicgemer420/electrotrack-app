"""Workout data models"""

from dataclasses import dataclass, field
from typing import Optional, Dict
from datetime import datetime
from enum import Enum


class WorkoutType(Enum):
    """Types of track and field workouts"""
    RUNNING = "running"
    SPRINTING = "sprinting"
    DISTANCE = "distance"
    INTERVAL = "interval"
    ENDURANCE = "endurance"
    SPEED_WORK = "speed_work"
    CROSS_TRAINING = "cross_training"


@dataclass
class WorkoutMetrics:
    """Biometric and performance metrics during workout"""
    duration_minutes: float
    average_heart_rate_bpm: int
    max_heart_rate_bpm: Optional[int] = None
    pre_workout_weight_kg: Optional[float] = None
    post_workout_weight_kg: Optional[float] = None
    fluid_intake_liters: float = 0.0
    workout_type: WorkoutType = WorkoutType.RUNNING
    distance_km: Optional[float] = None
    intensity_level: str = "moderate"  # 'low', 'moderate', 'high', 'extreme'
    
    def calculate_weight_loss_kg(self) -> float:
        """Calculate weight loss during workout"""
        if self.pre_workout_weight_kg and self.post_workout_weight_kg:
            return self.pre_workout_weight_kg - self.post_workout_weight_kg
        return 0.0
    
    def calculate_net_fluid_loss_liters(self) -> float:
        """Calculate net fluid loss (weight loss + intake)"""
        weight_loss_liters = self.calculate_weight_loss_kg()  # 1 kg ≈ 1 L
        return weight_loss_liters - self.fluid_intake_liters
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'duration_minutes': self.duration_minutes,
            'average_heart_rate_bpm': self.average_heart_rate_bpm,
            'max_heart_rate_bpm': self.max_heart_rate_bpm,
            'pre_workout_weight_kg': self.pre_workout_weight_kg,
            'post_workout_weight_kg': self.post_workout_weight_kg,
            'fluid_intake_liters': self.fluid_intake_liters,
            'workout_type': self.workout_type.value,
            'distance_km': self.distance_km,
            'intensity_level': self.intensity_level
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WorkoutMetrics':
        """Create from dictionary"""
        data = data.copy()
        if 'workout_type' in data:
            data['workout_type'] = WorkoutType(data['workout_type'])
        return cls(**data)


@dataclass
class EnvironmentalData:
    """Environmental conditions during workout"""
    temperature_fahrenheit: float
    humidity_percent: float
    location: Optional[str] = None  # e.g., "indoor", "outdoor", city name
    wind_speed_mph: Optional[float] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'temperature_fahrenheit': self.temperature_fahrenheit,
            'humidity_percent': self.humidity_percent,
            'location': self.location,
            'wind_speed_mph': self.wind_speed_mph
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'EnvironmentalData':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class Workout:
    """Complete workout record"""
    workout_id: str
    athlete_id: str
    metrics: WorkoutMetrics
    environmental: EnvironmentalData
    timestamp: datetime = field(default_factory=datetime.now)
    recommendations_applied: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'workout_id': self.workout_id,
            'athlete_id': self.athlete_id,
            'metrics': self.metrics.to_dict(),
            'environmental': self.environmental.to_dict(),
            'timestamp': self.timestamp.isoformat(),
            'recommendations_applied': self.recommendations_applied
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Workout':
        """Create from dictionary"""
        data = data.copy()
        data['metrics'] = WorkoutMetrics.from_dict(data['metrics'])
        data['environmental'] = EnvironmentalData.from_dict(data['environmental'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


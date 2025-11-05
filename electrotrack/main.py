"""Main application entry point for ElectroTrack"""

import sys
from typing import List, Optional, Tuple
from datetime import datetime

from .models.athlete import Athlete, AthleteProfile
from .models.workout import Workout, WorkoutMetrics, EnvironmentalData, WorkoutType
from .models.recommendation import HydrationRecommendation
from .ml.hydration_predictor import HydrationPredictor
from .processor.session_processor import SessionProcessor
from .api.weather_api import WeatherAPI


class ElectroTrack:
    """Main ElectroTrack system class"""
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        weather_api_key: Optional[str] = None
    ):
        """
        Initialize ElectroTrack system
        
        Args:
            model_path: Path to saved ML model (optional)
            weather_api_key: API key for weather service (optional)
        """
        self.predictor = HydrationPredictor(model_path)
        self.weather_api = WeatherAPI(weather_api_key) if weather_api_key else None
        self.processor = SessionProcessor(self.predictor, self.weather_api)
        self.athletes: dict[str, Athlete] = {}
        self.workouts: List[Workout] = []
    
    def register_athlete(
        self,
        athlete_id: str,
        profile: AthleteProfile
    ) -> Athlete:
        """
        Register a new athlete
        
        Args:
            athlete_id: Unique athlete identifier
            profile: Athlete physiological profile
            
        Returns:
            Registered Athlete object
        """
        athlete = Athlete(athlete_id=athlete_id, profile=profile)
        self.athletes[athlete_id] = athlete
        return athlete
    
    def get_recommendation(
        self,
        athlete_id: str,
        metrics: WorkoutMetrics,
        environmental: Optional[EnvironmentalData] = None,
        location: Optional[str] = None
    ) -> HydrationRecommendation:
        """
        Get hydration recommendation for a completed workout
        
        Args:
            athlete_id: Athlete identifier
            metrics: Workout metrics
            environmental: Environmental conditions (optional)
            location: Location for weather lookup (optional)
            
        Returns:
            HydrationRecommendation
        """
        athlete = self.athletes.get(athlete_id)
        if not athlete:
            raise ValueError(f"Athlete {athlete_id} not found")
        
        # Get environmental data if not provided
        if environmental is None:
            if self.weather_api and location:
                environmental = self.weather_api.get_current_conditions(location)
            else:
                environmental = EnvironmentalData(
                    temperature_fahrenheit=70.0,
                    humidity_percent=50.0,
                    location=location or "unknown"
                )
        
        # Generate recommendation
        recommendation = self.predictor.predict(athlete, metrics, environmental)
        
        # Store workout record
        workout = Workout(
            workout_id=f"{athlete_id}_{datetime.now().timestamp()}",
            athlete_id=athlete_id,
            metrics=metrics,
            environmental=environmental,
            recommendations_applied=recommendation.to_dict()
        )
        
        self.workouts.append(workout)
        athlete.workout_history.append(workout)
        
        return recommendation
    
    def start_workout_session(
        self,
        athlete_id: str,
        initial_metrics: WorkoutMetrics,
        environmental: Optional[EnvironmentalData] = None,
        location: Optional[str] = None
    ) -> str:
        """
        Start a real-time workout session
        
        Args:
            athlete_id: Athlete identifier
            initial_metrics: Initial workout metrics
            environmental: Environmental conditions (optional)
            location: Location for weather lookup (optional)
            
        Returns:
            Session ID
        """
        athlete = self.athletes.get(athlete_id)
        if not athlete:
            raise ValueError(f"Athlete {athlete_id} not found")
        
        return self.processor.start_session(
            athlete, initial_metrics, environmental, location
        )
    
    def update_workout_session(
        self,
        session_id: str,
        metrics: WorkoutMetrics
    ) -> Optional[HydrationRecommendation]:
        """
        Update active workout session and get recommendation
        
        Args:
            session_id: Session ID
            metrics: Updated metrics
            
        Returns:
            Recommendation if update triggered one, None otherwise
        """
        return self.processor.update_session(session_id, metrics)
    
    def end_workout_session(
        self,
        session_id: str,
        final_metrics: WorkoutMetrics
    ) -> Tuple[Workout, HydrationRecommendation]:
        """
        End workout session and get final recommendation
        
        Args:
            session_id: Session ID
            final_metrics: Final workout metrics
            
        Returns:
            Tuple of (Workout record, Final recommendation)
        """
        workout, recommendation = self.processor.end_session(session_id, final_metrics)
        
        # Store workout
        self.workouts.append(workout)
        athlete = self.athletes.get(workout.athlete_id)
        if athlete:
            athlete.workout_history.append(workout)
        
        return workout, recommendation
    
    def train_model(self, min_workouts: int = 10) -> dict:
        """
        Train the ML model on historical workout data
        
        Args:
            min_workouts: Minimum number of workouts required for training
            
        Returns:
            Training metrics
        """
        if len(self.workouts) < min_workouts:
            raise ValueError(
                f"Insufficient data for training. "
                f"Need at least {min_workouts} workouts, have {len(self.workouts)}"
            )
        
        athletes_list = list(self.athletes.values())
        return self.predictor.train(athletes_list, self.workouts)
    
    def save_model(self, model_path: str):
        """Save trained model to disk"""
        self.predictor.save_model(model_path)


def main():
    """Example usage of ElectroTrack system"""
    print("ElectroTrack - AI-Powered Hydration Monitoring System")
    print("=" * 60)
    
    # Initialize system
    system = ElectroTrack()
    
    # Example 1: High-intensity outdoor workout
    print("\n--- Example 1: High-Intensity 10K Run ---")
    
    # Register athlete
    athlete_profile = AthleteProfile(
        age=25,
        gender='M',
        weight_kg=70.0,
        height_cm=175.0,
        activity_level='competitive',
        baseline_heart_rate=60
    )
    athlete = system.register_athlete("athlete_001", athlete_profile)
    
    # Define workout metrics
    metrics = WorkoutMetrics(
        duration_minutes=45.0,
        average_heart_rate_bpm=175,
        max_heart_rate_bpm=185,
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
    
    print(f"\nRecommendation:")
    print(str(recommendation))
    
    # Example 2: Moderate indoor workout
    print("\n--- Example 2: Moderate Indoor Training ---")
    
    athlete_profile2 = AthleteProfile(
        age=22,
        gender='F',
        weight_kg=60.0,
        height_cm=165.0,
        activity_level='competitive',
        baseline_heart_rate=65
    )
    athlete2 = system.register_athlete("athlete_002", athlete_profile2)
    
    metrics2 = WorkoutMetrics(
        duration_minutes=45.0,
        average_heart_rate_bpm=140,
        pre_workout_weight_kg=60.0,
        post_workout_weight_kg=59.95,  # Minimal loss
        fluid_intake_liters=0.3,
        workout_type=WorkoutType.RUNNING,
        intensity_level='moderate'
    )
    
    environmental2 = EnvironmentalData(
        temperature_fahrenheit=70.0,
        humidity_percent=40.0,
        location="indoor"
    )
    
    recommendation2 = system.get_recommendation(
        "athlete_002", metrics2, environmental2
    )
    
    print(f"\nRecommendation:")
    print(str(recommendation2))
    
    print("\n" + "=" * 60)
    print("Examples completed successfully!")


if __name__ == "__main__":
    main()


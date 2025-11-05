"""ML-based hydration recommendation predictor"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os
from pathlib import Path

from ..models.athlete import Athlete
from ..models.workout import Workout, WorkoutMetrics, EnvironmentalData
from ..models.recommendation import HydrationRecommendation, DrinkType
from .feature_extractor import FeatureExtractor


class HydrationPredictor:
    """
    Machine learning model for predicting hydration needs.
    Uses Random Forest for interpretability and handling non-linear relationships.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize predictor
        
        Args:
            model_path: Path to saved model. If None, creates new model.
        """
        self.feature_extractor = FeatureExtractor()
        self.scaler = StandardScaler()
        self.model_volume = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.model_drink_type = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.is_trained = False
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def train(
        self,
        athletes: List[Athlete],
        workouts: List[Workout]
    ) -> Dict[str, float]:
        """
        Train the model on historical data
        
        Args:
            athletes: List of athletes with profiles
            workouts: List of completed workouts with outcomes
            
        Returns:
            Dictionary with training metrics
        """
        if not workouts:
            raise ValueError("No workout data provided for training")
        
        # Create athlete lookup
        athlete_dict = {a.athlete_id: a for a in athletes}
        
        # Extract features and targets
        X = []
        y_volume = []
        y_drink_type = []
        
        for workout in workouts:
            athlete = athlete_dict.get(workout.athlete_id)
            if not athlete:
                continue
            
            # Extract features
            features = self.feature_extractor.extract_features(
                athlete, workout.metrics, workout.environmental
            )
            X.append(features)
            
            # Calculate target values from workout outcomes
            # Volume: based on weight loss and fluid intake
            net_loss = workout.metrics.calculate_net_fluid_loss_liters()
            target_volume = max(0.0, net_loss * 1.5)  # Replace 150% of loss
            y_volume.append(target_volume)
            
            # Drink type: based on sodium loss (estimated from conditions)
            estimated_sodium_loss = self._estimate_sodium_loss(workout)
            if estimated_sodium_loss > 1500:  # High loss
                drink_type_value = 3.0  # High electrolyte
            elif estimated_sodium_loss > 800:  # Medium loss
                drink_type_value = 2.0  # Medium electrolyte
            elif estimated_sodium_loss > 400:  # Low loss
                drink_type_value = 1.0  # Low electrolyte
            else:
                drink_type_value = 0.0  # Water
            y_drink_type.append(drink_type_value)
        
        X = np.array(X)
        y_volume = np.array(y_volume)
        y_drink_type = np.array(y_drink_type)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train models
        self.model_volume.fit(X_scaled, y_volume)
        self.model_drink_type.fit(X_scaled, y_drink_type)
        
        self.is_trained = True
        
        # Calculate training metrics
        volume_pred = self.model_volume.predict(X_scaled)
        drink_pred = self.model_drink_type.predict(X_scaled)
        
        volume_mae = np.mean(np.abs(volume_pred - y_volume))
        drink_mae = np.mean(np.abs(drink_pred - y_drink_type))
        
        return {
            'volume_mae': volume_mae,
            'drink_type_mae': drink_mae,
            'samples_trained': len(X)
        }
    
    def predict(
        self,
        athlete: Athlete,
        metrics: WorkoutMetrics,
        environmental: EnvironmentalData
    ) -> HydrationRecommendation:
        """
        Predict hydration recommendation for a workout
        
        Args:
            athlete: Athlete profile
            metrics: Workout metrics
            environmental: Environmental conditions
            
        Returns:
            HydrationRecommendation
        """
        if not self.is_trained:
            # Use rule-based fallback if model not trained
            return self._rule_based_prediction(athlete, metrics, environmental)
        
        # Extract features
        features = self.feature_extractor.extract_features(
            athlete, metrics, environmental
        )
        features = features.reshape(1, -1)
        features_scaled = self.scaler.transform(features)
        
        # Predict
        volume_pred = self.model_volume.predict(features_scaled)[0]
        drink_type_pred = self.model_drink_type.predict(features_scaled)[0]
        
        # Ensure non-negative volume
        volume_pred = max(0.0, volume_pred)
        
        # Map drink type prediction to enum
        if drink_type_pred >= 2.5:
            drink_type = DrinkType.ELECTROLYTE_HIGH
        elif drink_type_pred >= 1.5:
            drink_type = DrinkType.ELECTROLYTE_MEDIUM
        elif drink_type_pred >= 0.5:
            drink_type = DrinkType.ELECTROLYTE_LOW
        else:
            drink_type = DrinkType.WATER
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            athlete, metrics, environmental, volume_pred, drink_type
        )
        
        # Determine urgency
        urgency = self._determine_urgency(metrics, environmental, volume_pred)
        
        # Generate future suggestions
        future_suggestions = self._generate_future_suggestions(
            athlete, metrics, environmental
        )
        
        # Determine timing (typically 30 minutes for normal, 15 for urgent)
        timing = 15 if urgency in ['high', 'urgent'] else 30
        
        return HydrationRecommendation(
            volume_liters=round(volume_pred, 2),
            drink_type=drink_type,
            timing_minutes=timing,
            reasoning=reasoning,
            urgency=urgency,
            future_suggestions=future_suggestions
        )
    
    def _rule_based_prediction(
        self,
        athlete: Athlete,
        metrics: WorkoutMetrics,
        environmental: EnvironmentalData
    ) -> HydrationRecommendation:
        """Fallback rule-based prediction when model not trained"""
        # Calculate fluid loss
        weight_loss = metrics.calculate_weight_loss_kg()
        
        # If weight loss data not available, estimate sweat volume
        if weight_loss <= 0:
            # Estimate sweat volume based on duration and conditions
            base_sweat_rate = athlete.profile.sweat_rate_liter_per_hour or 1.0  # L/hour
            
            # Adjust for temperature
            temp_factor = 1.0
            if environmental.temperature_fahrenheit > 85:
                temp_factor = 1.8
            elif environmental.temperature_fahrenheit > 80:
                temp_factor = 1.5
            elif environmental.temperature_fahrenheit > 75:
                temp_factor = 1.2
            
            # Adjust for intensity
            intensity_factor = {
                'low': 0.7,
                'moderate': 1.0,
                'high': 1.5,
                'extreme': 2.0
            }.get(metrics.intensity_level, 1.0)
            
            # Adjust for heart rate (if high, more sweating)
            hr_factor = 1.0
            if athlete.profile.baseline_heart_rate:
                hr_elevation = metrics.average_heart_rate_bpm - athlete.profile.baseline_heart_rate
                if hr_elevation > 50:
                    hr_factor = 1.3
                elif hr_elevation > 30:
                    hr_factor = 1.15
            
            estimated_sweat_rate = base_sweat_rate * temp_factor * intensity_factor * hr_factor
            estimated_sweat_volume = (metrics.duration_minutes / 60.0) * estimated_sweat_rate
            
            # Net loss = estimated sweat - fluid intake
            net_loss = estimated_sweat_volume - metrics.fluid_intake_liters
        else:
            # Use actual weight loss
            net_loss = weight_loss - metrics.fluid_intake_liters
        
        # Base recommendation: replace 150% of loss (minimum 0.2 L for any workout)
        volume = max(0.2, net_loss * 1.5)
        
        # Cap maximum volume at reasonable level (3 L)
        volume = min(volume, 3.0)
        
        # Estimate sodium loss
        estimated_sodium_loss = self._estimate_sodium_loss_from_metrics(
            metrics, environmental, athlete.profile
        )
        
        # Determine drink type
        if estimated_sodium_loss > 1500:
            drink_type = DrinkType.ELECTROLYTE_HIGH
            reasoning = "High sodium loss detected due to heat and intensity"
        elif estimated_sodium_loss > 800:
            drink_type = DrinkType.ELECTROLYTE_MEDIUM
            reasoning = "Moderate sodium loss due to workout conditions"
        elif estimated_sodium_loss > 400:
            drink_type = DrinkType.ELECTROLYTE_LOW
            reasoning = "Low sodium loss, light electrolyte supplementation recommended"
        else:
            drink_type = DrinkType.WATER
            reasoning = "Balanced hydration, minimal sodium loss"
        
        # Adjust reasoning based on conditions
        if environmental.temperature_fahrenheit > 80:
            reasoning += f" High temperature ({environmental.temperature_fahrenheit}°F) increases hydration needs."
        if metrics.average_heart_rate_bpm > 170:
            reasoning += f" High intensity workout (avg HR: {metrics.average_heart_rate_bpm} bpm) requires electrolyte replacement."
        
        urgency = self._determine_urgency(metrics, environmental, volume)
        future_suggestions = self._generate_future_suggestions(
            athlete, metrics, environmental
        )
        
        return HydrationRecommendation(
            volume_liters=round(volume, 2),
            drink_type=drink_type,
            timing_minutes=30,
            reasoning=reasoning,
            urgency=urgency,
            future_suggestions=future_suggestions
        )
    
    def _estimate_sodium_loss(self, workout: Workout) -> float:
        """Estimate sodium loss from workout"""
        return self._estimate_sodium_loss_from_metrics(
            workout.metrics,
            workout.environmental,
            None  # Will use defaults
        )
    
    def _estimate_sodium_loss_from_metrics(
        self,
        metrics: WorkoutMetrics,
        environmental: EnvironmentalData,
        profile
    ) -> float:
        """Estimate sodium loss in mg"""
        # Estimate sweat volume
        weight_loss = metrics.calculate_weight_loss_kg()
        if weight_loss > 0:
            sweat_volume = weight_loss  # 1 kg ≈ 1 L
        else:
            # Estimate based on duration and conditions
            sweat_rate = 1.0  # L/hour default
            if environmental.temperature_fahrenheit > 80:
                sweat_rate *= 1.5
            if metrics.intensity_level in ['high', 'extreme']:
                sweat_rate *= 1.3
            sweat_volume = (metrics.duration_minutes / 60.0) * sweat_rate
        
        # Sodium concentration in sweat (typically 500-1200 mg/L)
        base_sodium = 800.0  # mg/L
        if environmental.temperature_fahrenheit > 85:
            base_sodium *= 1.2  # Higher temp = more sodium loss
        if metrics.intensity_level in ['high', 'extreme']:
            base_sodium *= 1.3
        
        return sweat_volume * base_sodium
    
    def _generate_reasoning(
        self,
        athlete: Athlete,
        metrics: WorkoutMetrics,
        environmental: EnvironmentalData,
        volume: float,
        drink_type: DrinkType
    ) -> str:
        """Generate human-readable reasoning for recommendation"""
        reasons = []
        
        weight_loss = metrics.calculate_weight_loss_kg()
        if weight_loss > 0.5:
            reasons.append(f"Significant weight loss ({weight_loss:.2f} kg)")
        
        if environmental.temperature_fahrenheit > 85:
            reasons.append(f"High temperature ({environmental.temperature_fahrenheit}°F)")
        
        if metrics.average_heart_rate_bpm > 175:
            reasons.append(f"High intensity (avg HR: {metrics.average_heart_rate_bpm} bpm)")
        
        if drink_type != DrinkType.WATER:
            reasons.append("Electrolyte replacement needed due to sodium loss")
        
        if not reasons:
            reasons.append("Balanced hydration needs detected")
        
        return " ".join(reasons) + "."
    
    def _determine_urgency(
        self,
        metrics: WorkoutMetrics,
        environmental: EnvironmentalData,
        volume: float
    ) -> str:
        """Determine urgency level"""
        if volume > 1.0 or environmental.temperature_fahrenheit > 90:
            return "urgent"
        elif volume > 0.6 or metrics.average_heart_rate_bpm > 180:
            return "high"
        elif volume < 0.2:
            return "low"
        else:
            return "normal"
    
    def _generate_future_suggestions(
        self,
        athlete: Athlete,
        metrics: WorkoutMetrics,
        environmental: EnvironmentalData
    ) -> List[str]:
        """Generate suggestions for future workouts"""
        suggestions = []
        
        # Check for patterns that need adjustment
        if environmental.temperature_fahrenheit > 85 and metrics.fluid_intake_liters < 0.5:
            suggestions.append(
                "Consider pre-hydration before workouts in hot conditions (>85°F)"
            )
        
        if metrics.average_heart_rate_bpm > 175 and metrics.fluid_intake_liters == 0:
            suggestions.append(
                "For high-intensity workouts, consider carrying hydration during exercise"
            )
        
        weight_loss = metrics.calculate_weight_loss_kg()
        if weight_loss > 1.0:
            suggestions.append(
                "High fluid loss detected - monitor hydration throughout workout"
            )
        
        if not suggestions:
            suggestions.append("Continue current hydration routine")
        
        return suggestions
    
    def save_model(self, model_path: str):
        """Save trained model to disk"""
        Path(model_path).parent.mkdir(parents=True, exist_ok=True)
        model_data = {
            'scaler': self.scaler,
            'model_volume': self.model_volume,
            'model_drink_type': self.model_drink_type,
            'is_trained': self.is_trained
        }
        joblib.dump(model_data, model_path)
    
    def load_model(self, model_path: str):
        """Load trained model from disk"""
        model_data = joblib.load(model_path)
        self.scaler = model_data['scaler']
        self.model_volume = model_data['model_volume']
        self.model_drink_type = model_data['model_drink_type']
        self.is_trained = model_data['is_trained']


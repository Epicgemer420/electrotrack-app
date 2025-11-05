"""Real-time workout session processing"""

from typing import Optional, Dict, List
from typing import Tuple
from datetime import datetime
import threading
import time

from ..models.athlete import Athlete
from ..models.workout import Workout, WorkoutMetrics, EnvironmentalData
from ..models.recommendation import HydrationRecommendation
from ..ml.hydration_predictor import HydrationPredictor
from ..api.weather_api import WeatherAPI


class SessionProcessor:
    """
    Real-time processor for workout sessions.
    Monitors ongoing workouts and provides in-session feedback.
    """
    
    def __init__(
        self,
        predictor: HydrationPredictor,
        weather_api: Optional[WeatherAPI] = None
    ):
        """
        Initialize session processor
        
        Args:
            predictor: Trained hydration predictor
            weather_api: Optional weather API for real-time environmental data
        """
        self.predictor = predictor
        self.weather_api = weather_api
        self.active_sessions: Dict[str, 'WorkoutSession'] = {}
        self._lock = threading.Lock()
    
    def start_session(
        self,
        athlete: Athlete,
        initial_metrics: WorkoutMetrics,
        environmental: Optional[EnvironmentalData] = None,
        location: Optional[str] = None
    ) -> str:
        """
        Start a new workout session
        
        Args:
            athlete: Athlete starting workout
            initial_metrics: Initial workout metrics
            environmental: Environmental data (if None, will fetch from API)
            location: Location for weather API lookup
            
        Returns:
            Session ID
        """
        session_id = f"{athlete.athlete_id}_{datetime.now().timestamp()}"
        
        # Fetch environmental data if not provided
        if environmental is None and self.weather_api and location:
            environmental = self.weather_api.get_current_conditions(location)
        
        if environmental is None:
            # Default to moderate conditions
            environmental = EnvironmentalData(
                temperature_fahrenheit=70.0,
                humidity_percent=50.0,
                location=location or "unknown"
            )
        
        session = WorkoutSession(
            session_id=session_id,
            athlete=athlete,
            initial_metrics=initial_metrics,
            environmental=environmental
        )
        
        with self._lock:
            self.active_sessions[session_id] = session
        
        return session_id
    
    def update_session(
        self,
        session_id: str,
        metrics: WorkoutMetrics
    ) -> Optional[HydrationRecommendation]:
        """
        Update session with new metrics and get recommendation
        
        Args:
            session_id: Session ID
            metrics: Updated workout metrics
            
        Returns:
            HydrationRecommendation if significant change, None otherwise
        """
        with self._lock:
            session = self.active_sessions.get(session_id)
            if not session:
                return None
            
            session.update_metrics(metrics)
            
            # Only generate recommendation if significant update
            if session.should_recommend():
                recommendation = self.predictor.predict(
                    session.athlete,
                    session.current_metrics,
                    session.environmental
                )
                session.add_recommendation(recommendation)
                return recommendation
        
        return None
    
    def end_session(
        self,
        session_id: str,
        final_metrics: WorkoutMetrics
    ) -> Tuple[Workout, HydrationRecommendation]:
        """
        End workout session and generate final recommendation
        
        Args:
            session_id: Session ID
            final_metrics: Final workout metrics
            
        Returns:
            Tuple of (Workout record, Final recommendation)
        """
        with self._lock:
            session = self.active_sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            session.update_metrics(final_metrics)
            
            # Generate final recommendation
            recommendation = self.predictor.predict(
                session.athlete,
                session.current_metrics,
                session.environmental
            )
            
            # Create workout record
            workout = Workout(
                workout_id=session_id,
                athlete_id=session.athlete.athlete_id,
                metrics=session.current_metrics,
                environmental=session.environmental,
                timestamp=session.start_time,
                recommendations_applied=recommendation.to_dict()
            )
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            return workout, recommendation
    
    def get_session_status(self, session_id: str) -> Optional[Dict]:
        """Get current status of active session"""
        with self._lock:
            session = self.active_sessions.get(session_id)
            if not session:
                return None
            
            return {
                'session_id': session_id,
                'duration_minutes': (datetime.now() - session.start_time).total_seconds() / 60,
                'current_metrics': session.current_metrics.to_dict(),
                'recommendations_count': len(session.recommendations)
            }


class WorkoutSession:
    """Internal class for tracking active workout session"""
    
    def __init__(
        self,
        session_id: str,
        athlete: Athlete,
        initial_metrics: WorkoutMetrics,
        environmental: EnvironmentalData
    ):
        self.session_id = session_id
        self.athlete = athlete
        self.current_metrics = initial_metrics
        self.environmental = environmental
        self.start_time = datetime.now()
        self.recommendations: List[HydrationRecommendation] = []
        self.last_recommendation_time = None
    
    def update_metrics(self, metrics: WorkoutMetrics):
        """Update current metrics"""
        self.current_metrics = metrics
    
    def should_recommend(self) -> bool:
        """Determine if recommendation should be generated"""
        # Recommend every 15 minutes or on significant metric change
        if self.last_recommendation_time is None:
            return True
        
        time_since_last = (datetime.now() - self.last_recommendation_time).total_seconds()
        return time_since_last > 900  # 15 minutes
    
    def add_recommendation(self, recommendation: HydrationRecommendation):
        """Add recommendation to session"""
        self.recommendations.append(recommendation)
        self.last_recommendation_time = datetime.now()


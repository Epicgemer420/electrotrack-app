"""Athlete data models"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List
from datetime import datetime
import hashlib


@dataclass
class AthleteProfile:
    """Individual athlete physiological profile"""
    age: int
    gender: str  # 'M', 'F', or 'Other'
    weight_kg: float
    height_cm: float
    activity_level: str  # 'recreational', 'competitive', 'elite'
    sweat_rate_liter_per_hour: Optional[float] = None  # Personalized if known
    sodium_loss_rate_mg_per_liter: Optional[float] = None  # Personalized if known
    baseline_heart_rate: Optional[int] = None  # Resting heart rate
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            'age': self.age,
            'gender': self.gender,
            'weight_kg': self.weight_kg,
            'height_cm': self.height_cm,
            'activity_level': self.activity_level,
            'sweat_rate_liter_per_hour': self.sweat_rate_liter_per_hour,
            'sodium_loss_rate_mg_per_liter': self.sodium_loss_rate_mg_per_liter,
            'baseline_heart_rate': self.baseline_heart_rate
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AthleteProfile':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class Athlete:
    """Athlete entity with profile and history"""
    athlete_id: str
    profile: AthleteProfile
    created_at: datetime = field(default_factory=datetime.now)
    workout_history: List['Workout'] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary (excluding workout history for privacy)"""
        return {
            'athlete_id': self.athlete_id,
            'profile': self.profile.to_dict(),
            'created_at': self.created_at.isoformat()
        }
    
    def get_anonymous_id(self) -> str:
        """Generate anonymous ID for privacy-preserving analytics"""
        return hashlib.sha256(self.athlete_id.encode()).hexdigest()[:16]


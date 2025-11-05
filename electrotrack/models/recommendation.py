"""Hydration recommendation models"""

from dataclasses import dataclass
from typing import Optional, Dict, List
from datetime import timedelta
from enum import Enum


class DrinkType(Enum):
    """Types of hydration drinks"""
    WATER = "water"
    ELECTROLYTE_LOW = "electrolyte_low"  # Low sodium concentration
    ELECTROLYTE_MEDIUM = "electrolyte_medium"  # Medium sodium concentration
    ELECTROLYTE_HIGH = "electrolyte_high"  # High sodium concentration


@dataclass
class HydrationRecommendation:
    """Personalized hydration recommendation"""
    volume_liters: float
    drink_type: DrinkType
    timing_minutes: int  # Minutes from workout end to consume
    reasoning: str  # AI-generated explanation
    urgency: str = "normal"  # 'low', 'normal', 'high', 'urgent'
    additional_notes: Optional[str] = None
    future_suggestions: Optional[List[str]] = None  # AI suggestions for next workout
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'volume_liters': self.volume_liters,
            'drink_type': self.drink_type.value,
            'timing_minutes': self.timing_minutes,
            'reasoning': self.reasoning,
            'urgency': self.urgency,
            'additional_notes': self.additional_notes,
            'future_suggestions': self.future_suggestions
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'HydrationRecommendation':
        """Create from dictionary"""
        data = data.copy()
        data['drink_type'] = DrinkType(data['drink_type'])
        return cls(**data)
    
    def __str__(self) -> str:
        """Human-readable format"""
        drink_name = {
            DrinkType.WATER: "water",
            DrinkType.ELECTROLYTE_LOW: "low-sodium electrolyte drink",
            DrinkType.ELECTROLYTE_MEDIUM: "medium-sodium electrolyte drink",
            DrinkType.ELECTROLYTE_HIGH: "high-sodium electrolyte drink"
        }
        
        output = f"Recommended: {self.volume_liters:.2f} L of {drink_name[self.drink_type]}"
        output += f" within {self.timing_minutes} minutes post-workout.\n"
        output += f"Reason: {self.reasoning}"
        
        if self.future_suggestions:
            output += "\n\nFuture suggestions:\n"
            for suggestion in self.future_suggestions:
                output += f"- {suggestion}\n"
        
        return output


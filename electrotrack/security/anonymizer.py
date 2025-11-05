"""Data anonymization for privacy-preserving analytics"""

import hashlib
from typing import Dict, Any
from ..models.athlete import Athlete


def anonymize_athlete_data(athlete: Athlete) -> Dict[str, Any]:
    """
    Create anonymized version of athlete data for analytics
    
    Args:
        athlete: Athlete object
        
    Returns:
        Dictionary with anonymized data (no PII)
    """
    return {
        'anonymous_id': athlete.get_anonymous_id(),
        'age_range': _get_age_range(athlete.profile.age),
        'gender': athlete.profile.gender,  # Can be further anonymized if needed
        'weight_range': _get_weight_range(athlete.profile.weight_kg),
        'height_range': _get_height_range(athlete.profile.height_cm),
        'activity_level': athlete.profile.activity_level,
        # No specific identifiers
    }


def _get_age_range(age: int) -> str:
    """Convert age to range for anonymization"""
    if age < 18:
        return "under_18"
    elif age < 25:
        return "18-24"
    elif age < 35:
        return "25-34"
    elif age < 45:
        return "35-44"
    elif age < 55:
        return "45-54"
    else:
        return "55+"


def _get_weight_range(weight_kg: float) -> str:
    """Convert weight to range for anonymization"""
    ranges = [
        (0, 50, "under_50kg"),
        (50, 60, "50-60kg"),
        (60, 70, "60-70kg"),
        (70, 80, "70-80kg"),
        (80, 90, "80-90kg"),
        (90, 100, "90-100kg"),
        (100, float('inf'), "over_100kg")
    ]
    
    for min_w, max_w, label in ranges:
        if min_w <= weight_kg < max_w:
            return label
    
    return "unknown"


def _get_height_range(height_cm: float) -> str:
    """Convert height to range for anonymization"""
    ranges = [
        (0, 150, "under_150cm"),
        (150, 160, "150-160cm"),
        (160, 170, "160-170cm"),
        (170, 180, "170-180cm"),
        (180, 190, "180-190cm"),
        (190, float('inf'), "over_190cm")
    ]
    
    for min_h, max_h, label in ranges:
        if min_h <= height_cm < max_h:
            return label
    
    return "unknown"


import streamlit as st
import requests
import os

# Get API URL from environment variable or use default
API_BASE_URL = os.getenv("ELECTROTRACK_API_URL", "http://localhost:8000")

st.title("ElectroTrack - Hydration Advisor")

# Sidebar for athlete registration
st.sidebar.header("Athlete Registration")
register_athlete = st.sidebar.checkbox("Register New Athlete")

if register_athlete:
    athlete_id_reg = st.sidebar.text_input("Athlete ID", "athlete_001")
    age = st.sidebar.number_input("Age", min_value=1, max_value=100, value=25)
    gender = st.sidebar.selectbox("Gender", ["M", "F", "Other"])
    weight_kg = st.sidebar.number_input("Weight (kg)", min_value=30.0, value=70.0)
    height_cm = st.sidebar.number_input("Height (cm)", min_value=100.0, value=175.0)
    activity_level = st.sidebar.selectbox("Activity Level", ["recreational", "competitive", "elite"])
    baseline_hr = st.sidebar.number_input("Baseline Heart Rate (bpm)", min_value=40, max_value=100, value=60)
    
    if st.sidebar.button("Register Athlete"):
        url = f"{API_BASE_URL}/athletes/register"
        payload = {
            "athlete_id": athlete_id_reg,
            "age": age,
            "gender": gender,
            "weight_kg": weight_kg,
            "height_cm": height_cm,
            "activity_level": activity_level,
            "baseline_heart_rate": baseline_hr
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            st.sidebar.success("Athlete registered successfully!")
        else:
            st.sidebar.error(f"Error: {response.text}")

# Main form input
st.header("Workout Information")
athlete_id = st.text_input("Athlete ID", "athlete_001")
col1, col2 = st.columns(2)

with col1:
    duration = st.number_input("Workout Duration (minutes)", min_value=1, value=45)
    avg_hr = st.number_input("Average Heart Rate (bpm)", min_value=50, max_value=220, value=150)
    max_hr = st.number_input("Max Heart Rate (bpm)", min_value=50, max_value=220, value=None)
    temp = st.number_input("Temperature (°F)", value=75.0)
    humidity = st.number_input("Humidity (%)", min_value=0, max_value=100, value=50)

with col2:
    pre_weight = st.number_input("Pre-Workout Weight (kg)", min_value=0.0, value=None)
    post_weight = st.number_input("Post-Workout Weight (kg)", min_value=0.0, value=None)
    fluid_intake = st.number_input("Fluid Intake During Workout (L)", min_value=0.0, value=0.0)
    workout_type = st.selectbox("Workout Type", ["running", "sprinting", "distance", "interval", "endurance", "speed_work", "cross_training"])
    intensity = st.selectbox("Intensity Level", ["low", "moderate", "high", "extreme"])

distance = st.number_input("Distance (km) - Optional", min_value=0.0, value=None)

if st.button("Get Hydration Recommendation"):
    # Prepare payload
    payload = {
        "athlete_id": athlete_id,
        "duration_minutes": duration,
        "average_heart_rate_bpm": avg_hr,
        "temperature_fahrenheit": temp,
        "humidity_percent": humidity,
        "fluid_intake_liters": fluid_intake,
        "workout_type": workout_type,
        "intensity_level": intensity
    }
    
    # Add optional fields if provided
    if max_hr is not None:
        payload["max_heart_rate_bpm"] = int(max_hr)
    if pre_weight is not None:
        payload["pre_workout_weight_kg"] = pre_weight
    if post_weight is not None:
        payload["post_workout_weight_kg"] = post_weight
    if distance is not None:
        payload["distance_km"] = distance
    
    # Call backend API
    url = f"{API_BASE_URL}/recommend"
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        rec = response.json()
        
        # Display recommendation
        drink_type_display = {
            "water": "water",
            "electrolyte_low": "low-sodium electrolyte drink",
            "electrolyte_medium": "medium-sodium electrolyte drink",
            "electrolyte_high": "high-sodium electrolyte drink"
        }
        
        st.success(f"🍼 Drink **{rec['volume_liters']} L** of **{drink_type_display.get(rec['drink_type'], rec['drink_type'])}** within **{rec['timing_minutes']} minutes** post-workout")
        
        st.info(f"**Reasoning:** {rec['reasoning']}")
        
        if rec.get("urgency"):
            urgency_colors = {
                "urgent": "🔴",
                "high": "🟠",
                "normal": "🟡",
                "low": "🟢"
            }
            st.write(f"**Urgency:** {urgency_colors.get(rec['urgency'], '')} {rec['urgency'].upper()}")
        
        if rec.get("future_suggestions"):
            st.write("**Future Suggestions:**")
            for suggestion in rec["future_suggestions"]:
                st.write(f"- {suggestion}")
    else:
        error_msg = response.text
        if "not found" in error_msg.lower():
            st.error(f"❌ Athlete not registered! Please register the athlete first using the sidebar.")
        else:
            st.error(f"❌ Error: {error_msg}")

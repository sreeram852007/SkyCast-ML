import requests
import pandas as pd
import numpy as np
import xgboost as xgb
from pathlib import Path

# Load the model once when the script starts
MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "global_xgboost_weather.json"
model = xgb.XGBRegressor()
model.load_model(MODEL_PATH)

def get_city_options(city_name: str):
    """Uses Open-Meteo Geocoding API to find up to 5 matches for any city in the world."""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=5&language=en&format=json"
    response = requests.get(url).json()
    
    if "results" not in response:
        return []
        
    options = []
    for result in response["results"]:
        # Create a readable label like "Kerala, India" or "Kerala, Finland"
        label = f"{result['name']}, {result.get('country', 'Unknown')}"
        options.append({
            "label": label,
            "lat": result["latitude"],
            "lon": result["longitude"],
            "country": result.get("country", "Unknown"),
            "name": result["name"]
        })
    return options

def predict_tomorrow(lat: float, lon: float, name: str, country: str):
    """Fetches recent data and predicts tomorrow's mean temperature based on exact coordinates."""
    # Fetch past 7 days of weather to calculate our lags
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&past_days=7&daily=temperature_2m_mean&timezone=auto"
    response = requests.get(url).json()
    
    # Extract the past 7 days of temperatures
    temps = response["daily"]["temperature_2m_mean"]
    
    # We need exactly 7 days to calculate the rolling average and lags
    if len(temps) < 7 or None in temps:
        return {"error": "Not enough recent data available for this location."}

    # Calculate features for the latest available day (today)
    today_temp = temps[-1]
    lag_1 = temps[-1]
    lag_2 = temps[-2]
    lag_3 = temps[-3]
    rolling_7 = sum(temps) / 7.0
    
    # Get tomorrow's date for seasonal features (fixed deprecation warning)
    tomorrow = pd.to_datetime(response["daily"]["time"][-1]) + pd.Timedelta(days=1)
    day_of_year = tomorrow.day_of_year
    
    sin_day = np.sin(2 * np.pi * day_of_year / 365.25)
    cos_day = np.cos(2 * np.pi * day_of_year / 365.25)

    # Prepare the feature array in the exact order the model was trained on
    features = pd.DataFrame([{
        "latitude": lat,
        "longitude": lon,
        "sin_day": sin_day,
        "cos_day": cos_day,
        "temp_lag_1": lag_1,
        "temp_lag_2": lag_2,
        "temp_lag_3": lag_3,
        "temp_rolling_7": rolling_7
    }])

    # Make prediction
    prediction = model.predict(features)[0]

    # Clean up the city name in case the user typed "Kerala, India" instead of just "Kerala"
    clean_name = name.split(",")[0].strip().title()

    return {
        "city": clean_name,
        "country": country,
        "predicted_temp": round(float(prediction), 1),
        "today_temp": round(float(today_temp), 1),
        "date": tomorrow.strftime("%Y-%m-%d")
    }

# Test it!
if __name__ == "__main__":
    print("Testing city search for 'Kerala'...")
    opts = get_city_options("Kerala")
    print("Options found:", [o["label"] for o in opts])
    
    if opts:
        print(f"\nTesting prediction for {opts[0]['label']}...")
        result = predict_tomorrow(opts[0]['lat'], opts[0]['lon'], opts[0]['name'], opts[0]['country'])
        print(result)
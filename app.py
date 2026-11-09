import streamlit as st
from src.predictor import get_city_options, predict_tomorrow

# 1. Page Configuration
st.set_page_config(
    page_title="SkyCast-ML",
    page_icon="🌤️",
    layout="centered"
)

# 2. Caching for Speed
@st.cache_data(ttl=3600, show_spinner=False)
def get_cached_prediction(lat, lon, name, country):
    return predict_tomorrow(lat, lon, name, country)

# 3. UI Layout
st.title("🌤️ SkyCast-ML")
st.markdown("**Global Weather Prediction powered by Machine Learning**")
st.markdown("Enter any city in the world to get tomorrow's predicted average temperature.")

city_input = st.text_input("City Name", placeholder="e.g., London, Tokyo, Kerala...")

if city_input:
    # Fetch options dynamically as the user types
    options = get_city_options(city_input)
    
    if not options:
        st.error(f"Could not find any location named '{city_input}'.")
    else:
        # Create a dropdown menu for the user
        selected_label = st.selectbox("Select the correct location:", [opt["label"] for opt in options])
        
        # Find the selected location's data
        selected_data = next((opt for opt in options if opt["label"] == selected_label), None)
        
        if st.button("Predict Weather", type="primary"):
            with st.spinner("Fetching global weather data..."):
                result = get_cached_prediction(
                    selected_data["lat"], 
                    selected_data["lon"], 
                    selected_data["name"], 
                    selected_data["country"]
                )
                
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.success(f"Prediction for **{result['city']}, {result['country']}** on {result['date']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(label="Tomorrow's Predicted Temp", value=f"{result['predicted_temp']} °C")
                    with col2:
                        st.metric(label="Today's Average Temp", value=f"{result['today_temp']} °C")
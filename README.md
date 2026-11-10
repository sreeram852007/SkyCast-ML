# 🌤️ SkyCast-ML

A fast, global Machine Learning weather forecasting application. 

**🔗 [Try the Live Web App Here](https://skycast-ml.streamlit.app/)**

## 🧠 About the Project
This project predicts tomorrow's average temperature for **any city in the world**. It uses a custom-trained XGBoost model that leverages historical weather patterns, geography (latitude/longitude), and seasonality to make accurate predictions in milliseconds.

## 📊 Model Performance
* **Algorithm:** XGBoost Regressor
* **MAE (Mean Absolute Error):** 1.33 °C
* **Baseline comparison:** Outperformed the Persistence Baseline (1.45 °C) on a time-based test split.
* **Training Data:** 14,500+ days of historical weather data across 8 globally diverse cities (from open-meteo).

## ⚙️ Tech Stack
* **Backend/ML:** Python, XGBoost, Pandas, Scikit-Learn
* **Frontend:** Streamlit (Community Cloud)
* **Data Sources:** Open-Meteo Historical Archive API & Geocoding API

## 🚀 How it Works
1. The user enters a city name.
2. The app fetches live coordinates and the past 7 days of weather data via the Open-Meteo API.
3. The pipeline dynamically engineers features (lags, rolling averages, sine/cosine seasonality).
4. The XGBoost model predicts tomorrow's temperature.
5. Results are cached for 1 hour to ensure blazing-fast response times for repeated queries.

## 💻 Run Locally
1. Clone the repo: `git clone https://github.com/sreeram852007/SkyCast-ML.git`
2. Create a virtual environment: `py -3.12 -m venv .venv`
3. Activate it: `.\.venv\Scripts\Activate.ps1`
4. Install dependencies: `python -m pip install -r requirements.txt`
5. Run the app: `streamlit run app.py`
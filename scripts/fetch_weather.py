"""Fetch historical daily weather from Open-Meteo for a set of global cities."""

from __future__ import annotations

import argparse
import time
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import requests

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

DAILY_VARS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "precipitation_sum",
    "rain_sum",
    "snowfall_sum",
    "wind_speed_10m_max",
    "wind_gusts_10m_max",
    "wind_direction_10m_dominant",
    "shortwave_radiation_sum",
    "et0_fao_evapotranspiration",
]

# slug -> (latitude, longitude)
CITIES = {
    "kolkata":   (22.5726,  88.3639),
    "london":    (51.5074,  -0.1278),
    "new_york":  (40.7128, -74.0060),
    "tokyo":     (35.6762, 139.6503),
    "sydney":    (-33.8688, 151.2093),
    "nairobi":   (-1.2921,  36.8219),
    "sao_paulo": (-23.5505, -46.6333),
    "reykjavik": (64.1466, -21.9426),
}

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


def fetch_city(slug: str, lat: float, lon: float,
               start: date, end: date,
               retries: int = 3, timeout: int = 30) -> pd.DataFrame:
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "daily": ",".join(DAILY_VARS),
        "timezone": "auto",
    }
    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(ARCHIVE_URL, params=params, timeout=timeout)
            if resp.status_code == 429:
                raise requests.HTTPError("429 rate limited")
            resp.raise_for_status()
            payload = resp.json()
            if "daily" not in payload:
                raise ValueError(f"unexpected payload keys: {list(payload)}")
            df = pd.DataFrame(payload["daily"]).rename(columns={"time": "date"})
            df["date"] = pd.to_datetime(df["date"])
            df.insert(0, "city", slug)
            df.insert(1, "latitude", payload["latitude"])
            df.insert(2, "longitude", payload["longitude"])
            return df
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            # Changed: wait 60s, 120s, 180s instead of 2s, 4s, 8s
            wait = 60 * attempt  
            print(f"  retry {attempt}/{retries} in {wait}s ({exc})")
            time.sleep(wait)
    raise RuntimeError(f"{slug}: failed after {retries} attempts") from last_exc


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=date.fromisoformat,
                        help="YYYY-MM-DD (default: 5 years before --end)")
    parser.add_argument("--end", type=date.fromisoformat,
                        help="YYYY-MM-DD (default: 6 days ago; archive lags)")
    parser.add_argument("--cities", nargs="*", choices=sorted(CITIES),
                        help="subset of cities (default: all)")
    args = parser.parse_args()

    end = args.end or (date.today() - timedelta(days=6))
    start = args.start or (end - timedelta(days=365 * 5))
    if start >= end:
        parser.error("--start must be before --end")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    targets = {k: CITIES[k] for k in (args.cities or CITIES)}

    print(f"Range: {start} -> {end}   Cities: {len(targets)}")
    for slug, (lat, lon) in targets.items():
        print(f"{slug} ({lat}, {lon})")
        df = fetch_city(slug, lat, lon, start, end)
        out = RAW_DIR / f"{slug}_daily.csv"
        df.to_csv(out, index=False)
        print(f"  {len(df)} rows -> {out.relative_to(RAW_DIR.parents[1])}")
        # Changed: 5 seconds between cities to avoid triggering the rate limit
        time.sleep(5.0)  


if __name__ == "__main__":
    main()
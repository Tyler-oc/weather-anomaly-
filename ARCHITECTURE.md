# Architecture

## Overview

Weather anomaly detection and prediction system. Fetches historical weather data from Open-Meteo, classifies anomalies via z-score analysis, trains a random forest classifier, and runs a periodic prediction job.

Two anomaly types are planned:
- **Type 1 (Seasonal):** Deviation from historical norms for that time of year/location (e.g., unusually hot January). Classified via z-score against seasonal baseline; predicted using ~3 months of prior data.
- **Type 2 (Delta):** Rapid change from previous days (e.g., sudden temperature swing). Classified via rolling-window z-score; predicted using ~1–2 weeks of prior data.

Current implementation targets Type 1 (temperature anomalies) first.

---

## Directory Layout

```
weather-anomaly/
├── main.py                    # Top-level entry point (cron/scheduled job runner)
├── train.py                   # Entry point for model training pipeline
├── plan.md                    # Project planning notes
├── requirements.txt           # Python dependencies
├── pyproject.toml             # Project metadata, tool config, pytest settings
├── notebooks/
│   └── exploration.ipynb      # EDA: covariance matrices, variable selection
├── tests/
│   └── data/
│       └── test_fetch.py      # Unit tests for fetch.py (build_params, parse, save/load, fetch_weather)
└── src/
    ├── main.py                # Orchestrates the full inference pipeline
    ├── data/
    │   ├── fetch.py           # Fetches raw weather data from Open-Meteo archive API; exposes fetch_weather() and load_weather()
    │   └── injest.py          # Cleans data, engineers features, runs z-score anomaly labeling
    ├── analysis/
    │   └── zscore.py          # Z-score utilities for anomaly classification
    ├── models/
    │   ├── train.py           # Trains random forest classifier; saves model/scaler/features to .pkl
    │   ├── predict.py         # Loads saved model artifacts and produces anomaly predictions
    │   └── evaluate.py        # Model evaluation metrics and reporting
    └── utils/
        └── config.py          # Shared configuration (API params, thresholds, paths, variable lists)
```

---

## Data Flow

```
Open-Meteo API
    └─► src/data/fetch.py          # Raw hourly + daily JSON → DataFrame
            └─► src/data/injest.py # Feature engineering + z-score anomaly labels → labeled DataFrame
                    └─► src/models/train.py   # Train random forest → model.pkl, scaler.pkl, features.pkl
                                └─► src/models/predict.py  # Load artifacts → anomaly probability scores
```

---

## Key Variables

Defined in `src/utils/config.py`. Sourced from Open-Meteo.

**Hourly:** `temperature_2m`, `relative_humidity_2m`, `precipitation`, `snowfall`, `snow_depth`, `windspeed_10m`, `wind_gusts_10m`, `wind_direction_10m`, `pressure_msl`, `cloud_cover`, `visibility`, `weathercode`, `vapour_pressure_deficit`

**Daily:** `temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`, `snowfall_sum`, `windspeed_10m_max`, `windgusts_10m_max`, `precipitation_hours`, `sunshine_duration`, `uv_index_max`, `weathercode`

---

## Model Artifacts

Saved to disk after training (path configured in `src/utils/config.py`):
- `model.pkl` — trained sklearn RandomForestClassifier
- `scaler.pkl` — fitted feature scaler
- `features.pkl` — ordered list of feature names used during training

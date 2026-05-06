import os
from datetime import date

import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry

from src.utils.config import (
    DATA_DIR,
    DAILY_VARS,
    DENVER_LAT,
    DENVER_LON,
    HISTORICAL_START,
    HOURLY_VARS,
    PRESSURE_LEVEL_VARS,
)

_BASE_URL = "https://archive-api.open-meteo.com/v1/archive"
_TIMEZONE = "America/Denver"
_ALL_HOURLY = HOURLY_VARS + PRESSURE_LEVEL_VARS


def _make_client() -> openmeteo_requests.Client:
    cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    return openmeteo_requests.Client(session=retry_session)


# Use when you need to customize the request before calling fetch_raw (e.g. different date range or location).
def build_params(start_date: str, end_date: str, lat: float, lon: float) -> dict:
    return {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": list(_ALL_HOURLY),
        "daily": list(DAILY_VARS),
        "timezone": _TIMEZONE,
    }


# Use when you need the raw API response object to pass to parse_hourly/parse_daily yourself, or to inspect fields not yet parsed.
def fetch_raw(params: dict):
    client = _make_client()
    responses = client.weather_api(_BASE_URL, params=params)
    return responses[0]


def _build_time_index(obj) -> pd.DatetimeIndex:
    return pd.date_range(
        start=pd.to_datetime(obj.Time(), unit="s", utc=True),
        end=pd.to_datetime(obj.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=obj.Interval()),
        inclusive="left",
        name="time",
    )


# Use after fetch_raw to extract hourly variables (temperature, wind, pressure-level, etc.) into a DataFrame.
def parse_hourly(response) -> pd.DataFrame:
    hourly = response.Hourly()
    data = {var: hourly.Variables(i).ValuesAsNumpy() for i, var in enumerate(_ALL_HOURLY)}
    return pd.DataFrame(data, index=_build_time_index(hourly))


# Use after fetch_raw to extract daily summary variables (precip, min/max temp, etc.) into a DataFrame.
def parse_daily(response) -> pd.DataFrame:
    daily = response.Daily()
    data = {var: daily.Variables(i).ValuesAsNumpy() for i, var in enumerate(DAILY_VARS)}
    return pd.DataFrame(data, index=_build_time_index(daily))


# Use to persist both DataFrames to disk after fetching, so subsequent runs can use load_weather instead of hitting the API.
def save_weather(hourly_df: pd.DataFrame, daily_df: pd.DataFrame) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    hourly_df.to_csv(os.path.join(DATA_DIR, "hourly.csv"))
    daily_df.to_csv(os.path.join(DATA_DIR, "daily.csv"))


# Use when data has already been fetched and saved — returns (hourly_df, daily_df) from disk without an API call.
def load_weather() -> tuple[pd.DataFrame, pd.DataFrame]:
    hourly_path = os.path.join(DATA_DIR, "hourly.csv")
    daily_path = os.path.join(DATA_DIR, "daily.csv")
    if not os.path.exists(hourly_path) or not os.path.exists(daily_path):
        raise FileNotFoundError(f"Weather data not found in '{DATA_DIR}'. Run fetch_weather() first.")
    hourly_df = pd.read_csv(hourly_path, index_col="time", parse_dates=True)
    daily_df = pd.read_csv(daily_path, index_col="time", parse_dates=True)
    return hourly_df, daily_df


# Use as the single entry point for ingestion — fetches, parses, saves, and returns (hourly_df, daily_df) in one call.
# Prefer this over calling build_params/fetch_raw/parse_*/save_weather separately unless you need to customize a step.
def fetch_weather(
    start_date: str = HISTORICAL_START,
    end_date: str | None = None,
    lat: float = DENVER_LAT,
    lon: float = DENVER_LON,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if end_date is None:
        end_date = date.today().isoformat()
    params = build_params(start_date, end_date, lat, lon)
    response = fetch_raw(params)
    hourly_df = parse_hourly(response)
    daily_df = parse_daily(response)
    save_weather(hourly_df, daily_df)
    return hourly_df, daily_df

from datetime import date, datetime, timezone
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from src.data.fetch import (
    build_params,
    fetch_raw,
    fetch_weather,
    load_weather,
    parse_daily,
    parse_hourly,
    save_weather,
)
from src.utils.config import (
    DAILY_VARS,
    DENVER_LAT,
    DENVER_LON,
    HISTORICAL_START,
    HOURLY_VARS,
    PRESSURE_LEVEL_VARS,
)

_ALL_HOURLY = HOURLY_VARS + PRESSURE_LEVEL_VARS
_BASE_TS = int(datetime(2024, 1, 1, tzinfo=timezone.utc).timestamp())


def _make_mock_response(n_hours=48, n_days=2):
    """Mock openmeteo SDK response replicating the Variables(i).ValuesAsNumpy() interface."""
    hourly_var_mocks = []
    for i in range(len(_ALL_HOURLY)):
        m = MagicMock()
        m.ValuesAsNumpy.return_value = np.full(n_hours, float(i), dtype=np.float64)
        hourly_var_mocks.append(m)

    mock_hourly = MagicMock()
    mock_hourly.Time.return_value = _BASE_TS
    mock_hourly.TimeEnd.return_value = _BASE_TS + n_hours * 3600
    mock_hourly.Interval.return_value = 3600
    mock_hourly.Variables.side_effect = lambda i: hourly_var_mocks[i]

    daily_var_mocks = []
    for i in range(len(DAILY_VARS)):
        m = MagicMock()
        m.ValuesAsNumpy.return_value = np.full(n_days, float(i), dtype=np.float64)
        daily_var_mocks.append(m)

    mock_daily = MagicMock()
    mock_daily.Time.return_value = _BASE_TS
    mock_daily.TimeEnd.return_value = _BASE_TS + n_days * 86400
    mock_daily.Interval.return_value = 86400
    mock_daily.Variables.side_effect = lambda i: daily_var_mocks[i]

    mock_response = MagicMock()
    mock_response.Hourly.return_value = mock_hourly
    mock_response.Daily.return_value = mock_daily
    return mock_response


def _mock_client(response):
    """Return a patched _make_client that yields a client whose weather_api returns response."""
    mock_client = MagicMock()
    mock_client.weather_api.return_value = [response]
    return MagicMock(return_value=mock_client), mock_client


# ---------------------------------------------------------------------------
# build_params
# ---------------------------------------------------------------------------

class TestBuildParams:
    def test_required_keys_present(self):
        params = build_params("2024-01-01", "2024-01-31", DENVER_LAT, DENVER_LON)
        for key in ("latitude", "longitude", "start_date", "end_date", "hourly", "daily", "timezone"):
            assert key in params

    def test_lat_lon_values(self):
        params = build_params("2024-01-01", "2024-01-31", 40.0, -105.0)
        assert params["latitude"] == 40.0
        assert params["longitude"] == -105.0

    def test_date_values(self):
        params = build_params("2024-01-01", "2024-03-31", DENVER_LAT, DENVER_LON)
        assert params["start_date"] == "2024-01-01"
        assert params["end_date"] == "2024-03-31"

    def test_hourly_is_list_containing_all_vars(self):
        params = build_params("2024-01-01", "2024-01-31", DENVER_LAT, DENVER_LON)
        assert isinstance(params["hourly"], list)
        for var in _ALL_HOURLY:
            assert var in params["hourly"]

    def test_daily_is_list_containing_all_vars(self):
        params = build_params("2024-01-01", "2024-01-31", DENVER_LAT, DENVER_LON)
        assert isinstance(params["daily"], list)
        for var in DAILY_VARS:
            assert var in params["daily"]

    def test_hourly_has_no_duplicates(self):
        params = build_params("2024-01-01", "2024-01-31", DENVER_LAT, DENVER_LON)
        assert len(params["hourly"]) == len(set(params["hourly"]))


# ---------------------------------------------------------------------------
# parse_hourly
# ---------------------------------------------------------------------------

class TestParseHourly:
    def test_returns_dataframe(self):
        df = parse_hourly(_make_mock_response())
        assert isinstance(df, pd.DataFrame)

    def test_datetime_index(self):
        df = parse_hourly(_make_mock_response())
        assert isinstance(df.index, pd.DatetimeIndex)

    def test_index_is_utc(self):
        df = parse_hourly(_make_mock_response())
        assert df.index.tz is not None

    def test_index_name(self):
        df = parse_hourly(_make_mock_response())
        assert df.index.name == "time"

    def test_all_vars_present(self):
        df = parse_hourly(_make_mock_response())
        for var in _ALL_HOURLY:
            assert var in df.columns

    def test_time_not_a_column(self):
        df = parse_hourly(_make_mock_response())
        assert "time" not in df.columns

    def test_row_count(self):
        df = parse_hourly(_make_mock_response(n_hours=72))
        assert len(df) == 72

    def test_variables_assigned_in_order(self):
        df = parse_hourly(_make_mock_response())
        # _make_mock_response fills var i with float(i), so check first and last
        assert (df[_ALL_HOURLY[0]] == 0.0).all()
        assert (df[_ALL_HOURLY[-1]] == float(len(_ALL_HOURLY) - 1)).all()


# ---------------------------------------------------------------------------
# parse_daily
# ---------------------------------------------------------------------------

class TestParseDaily:
    def test_returns_dataframe(self):
        df = parse_daily(_make_mock_response())
        assert isinstance(df, pd.DataFrame)

    def test_datetime_index(self):
        df = parse_daily(_make_mock_response())
        assert isinstance(df.index, pd.DatetimeIndex)

    def test_index_is_utc(self):
        df = parse_daily(_make_mock_response())
        assert df.index.tz is not None

    def test_index_name(self):
        df = parse_daily(_make_mock_response())
        assert df.index.name == "time"

    def test_all_vars_present(self):
        df = parse_daily(_make_mock_response())
        for var in DAILY_VARS:
            assert var in df.columns

    def test_time_not_a_column(self):
        df = parse_daily(_make_mock_response())
        assert "time" not in df.columns

    def test_row_count(self):
        df = parse_daily(_make_mock_response(n_days=10))
        assert len(df) == 10

    def test_variables_assigned_in_order(self):
        df = parse_daily(_make_mock_response())
        assert (df[DAILY_VARS[0]] == 0.0).all()
        assert (df[DAILY_VARS[-1]] == float(len(DAILY_VARS) - 1)).all()


# ---------------------------------------------------------------------------
# fetch_raw
# ---------------------------------------------------------------------------

class TestFetchRaw:
    def test_returns_first_response(self):
        mock_response = _make_mock_response()
        mock_make_client, mock_client = _mock_client(mock_response)
        with patch("src.data.fetch._make_client", mock_make_client):
            result = fetch_raw({})
        assert result is mock_response

    def test_raises_on_api_error(self):
        mock_make_client = MagicMock()
        mock_make_client.return_value.weather_api.side_effect = Exception("API error")
        with patch("src.data.fetch._make_client", mock_make_client):
            with pytest.raises(Exception, match="API error"):
                fetch_raw({})

    def test_passes_params_to_weather_api(self):
        params = {"latitude": 39.7, "longitude": -104.9}
        mock_make_client, mock_client = _mock_client(_make_mock_response())
        with patch("src.data.fetch._make_client", mock_make_client):
            fetch_raw(params)
        assert mock_client.weather_api.call_args.kwargs["params"] == params


# ---------------------------------------------------------------------------
# save_weather / load_weather
# ---------------------------------------------------------------------------

class TestSaveAndLoadWeather:
    def test_round_trip(self, tmp_path):
        resp = _make_mock_response()
        hourly_df = parse_hourly(resp)
        daily_df = parse_daily(resp)

        with patch("src.data.fetch.DATA_DIR", str(tmp_path)):
            save_weather(hourly_df, daily_df)
            loaded_hourly, loaded_daily = load_weather()

        # CSV round-trip loses datetime resolution (s → us) and freq metadata; values are preserved
        pd.testing.assert_frame_equal(hourly_df, loaded_hourly, check_index_type=False, check_freq=False)
        pd.testing.assert_frame_equal(daily_df, loaded_daily, check_index_type=False, check_freq=False)

    def test_creates_data_dir_if_missing(self, tmp_path):
        subdir = tmp_path / "subdir"
        resp = _make_mock_response()
        with patch("src.data.fetch.DATA_DIR", str(subdir)):
            save_weather(parse_hourly(resp), parse_daily(resp))
        assert subdir.exists()

    def test_load_raises_when_files_missing(self, tmp_path):
        with patch("src.data.fetch.DATA_DIR", str(tmp_path)):
            with pytest.raises(FileNotFoundError):
                load_weather()


# ---------------------------------------------------------------------------
# fetch_weather
# ---------------------------------------------------------------------------

class TestFetchWeather:
    def test_returns_tuple_of_dataframes(self):
        mock_make_client, _ = _mock_client(_make_mock_response())
        with patch("src.data.fetch._make_client", mock_make_client):
            with patch("src.data.fetch.save_weather"):
                hourly_df, daily_df = fetch_weather("2024-01-01", "2024-01-02")
        assert isinstance(hourly_df, pd.DataFrame)
        assert isinstance(daily_df, pd.DataFrame)

    def test_end_date_defaults_to_today(self):
        today = date.today().isoformat()
        mock_make_client, mock_client = _mock_client(_make_mock_response())
        with patch("src.data.fetch._make_client", mock_make_client):
            with patch("src.data.fetch.save_weather"):
                fetch_weather("2024-01-01")
        params = mock_client.weather_api.call_args.kwargs["params"]
        assert params["end_date"] == today

    def test_uses_config_defaults_for_lat_lon_and_start(self):
        mock_make_client, mock_client = _mock_client(_make_mock_response())
        with patch("src.data.fetch._make_client", mock_make_client):
            with patch("src.data.fetch.save_weather"):
                fetch_weather()
        params = mock_client.weather_api.call_args.kwargs["params"]
        assert params["latitude"] == DENVER_LAT
        assert params["longitude"] == DENVER_LON
        assert params["start_date"] == HISTORICAL_START

    def test_calls_save_weather(self):
        mock_make_client, _ = _mock_client(_make_mock_response())
        with patch("src.data.fetch._make_client", mock_make_client):
            with patch("src.data.fetch.save_weather") as mock_save:
                fetch_weather("2024-01-01", "2024-01-02")
        mock_save.assert_called_once()

    def test_custom_lat_lon(self):
        mock_make_client, mock_client = _mock_client(_make_mock_response())
        with patch("src.data.fetch._make_client", mock_make_client):
            with patch("src.data.fetch.save_weather"):
                fetch_weather("2024-01-01", "2024-01-02", lat=51.5, lon=-0.1)
        params = mock_client.weather_api.call_args.kwargs["params"]
        assert params["latitude"] == 51.5
        assert params["longitude"] == -0.1

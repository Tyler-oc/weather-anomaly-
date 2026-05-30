from fetch import fetch_weather
import pandas as pd
from utils.config import HISTORICAL_START, DENVER_LAT, DENVER_LON
from datetime import datetime


# extract important hourly variables, create clean dataframe for training
def injest_hourly(hourly_df):
    return hourly_df


# extract important daily variables, create clean dataframe for training
def injest_daily(daily_df):
    # drop completely null rows and columns
    daily_df.dropna(how="all").dropna(axis="column", how="all")

    # drop columns that carry no meaning
    daily_df.drop(
        columns=["apparent_temperature_max", "apparent_temperature_min"]
    )  # more

    # make new columns
    return daily_df


def injest_weather_dfs():
    # end date defaults to now
    [hourly_df, daily_df] = fetch_weather(
        HISTORICAL_START, None, DENVER_LAT, DENVER_LON
    )
    injest_hourly(hourly_df)
    injest_daily(daily_df)

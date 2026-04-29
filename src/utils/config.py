DENVER_LAT = 39.7392
DENVER_LON = -104.9903

HISTORICAL_START = "2010-01-01"
FEATURE_WINDOW_DAYS = 30
ANOMALY_THRESHOLD_STD = 2.0
TARGET_HORIZON_DAYS = 1.0


ARTIFACTS_DIR = "artifacts/"
DATA_DIR = "data/"

HOURLY_VARS = [
    # Temperature & humidity
    "temperature_2m",           # primary thermal signal
    "apparent_temperature",     # feels-like (wind chill + humidity + radiation); anomalies here matter for human impact
    "dew_point_2m",             # encodes both temp and humidity in a single value; sharp drops signal air mass changes
    "relative_humidity_2m",

    # Precipitation & snow
    "precipitation",            # total liquid equivalent
    "rain",                     # large-scale stratiform rain, separated from convective showers
    "showers",                  # convective (thunderstorm-type) precip; useful for storm anomaly detection
    "snowfall",
    "snow_depth",               # accumulated on ground; slow-changing context signal

    # Wind
    "wind_speed_10m",
    "wind_speed_80m",           # boundary-layer wind aloft; separates surface drag from free-air flow
    "wind_gusts_10m",
    "wind_direction_10m",

    # Surface pressure
    "surface_pressure",         # actual pressure at elevation (Denver ~840 hPa baseline)
    "pressure_msl",             # sea-level-corrected; standard synoptic signal, better for cross-location comparison

    # Cloud cover (layered)
    "cloud_cover",              # total
    "cloud_cover_low",          # stratus/fog layer; fog and icing anomalies
    "cloud_cover_mid",          # altostratus; transition layer
    "cloud_cover_high",         # cirrus; jet stream and moisture transport signal

    # Atmospheric stability & other
    "cape",                     # convective available potential energy; high values precede severe storms
    "freezing_level_height",    # altitude of 0°C isotherm; controls rain/snow line, useful for winter anomalies
    "visibility",
    "vapour_pressure_deficit",  # combines temp and humidity into one heat/drought stress signal
    "weather_code",             # WMO categorical code; encodes dominant condition
]

# Pressure-level variables capture upper-atmosphere structure driving surface weather.
# 850 hPa (~1500 m): air mass temperature and moisture transport
# 500 hPa (~5500 m): mid-troposphere ridges and troughs, dominant synoptic pattern signal
# 300 hPa (~9000 m): jet stream level; wind anomalies here precede surface pattern shifts
PRESSURE_LEVEL_VARS = [
    "temperature_850hPa",
    "relative_humidity_850hPa",
    "wind_speed_850hPa",
    "geopotential_height_850hPa",   # height anomalies identify warm/cold ridges and troughs

    "temperature_500hPa",
    "wind_speed_500hPa",
    "geopotential_height_500hPa",   # classic weather-map level for ridge/trough analysis

    "wind_speed_300hPa",
    "geopotential_height_300hPa",   # jet stream position and intensity
]

DAILY_VARS = [
    # Temperature
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "apparent_temperature_max",     # felt heat extremes for impact-based anomaly detection
    "apparent_temperature_min",

    # Precipitation
    "precipitation_sum",
    "rain_sum",                     # separates liquid precip from snow in mixed events
    "snowfall_sum",
    "precipitation_hours",          # duration distinguishes prolonged events from brief bursts
    "precipitation_probability_max",

    # Wind
    "wind_speed_10m_max",
    "wind_gusts_10m_max",
    "wind_direction_10m_dominant",

    # Solar & sky
    "sunshine_duration",            # clear vs overcast day; inversely correlated with cloud_cover anomalies
    "uv_index_max",                 # solar intensity; anomalously high values signal unusual atmospheric clarity

    # Condition summary
    "weather_code",                 # dominant WMO condition for the day
]
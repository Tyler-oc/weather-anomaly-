Hourly df:
=== Hourly nulls ===
wind_speed_80m 143280
cape 143280
freezing_level_height 143280
visibility 143280
temperature_850hPa 143280
relative_humidity_850hPa 143280
wind_speed_850hPa 143280
geopotential_height_850hPa 143280
temperature_500hPa 143280
wind_speed_500hPa 143280
geopotential_height_500hPa 143280
wind_speed_300hPa 143280
geopotential_height_300hPa 143280

--- remove these rows, the others are fine

daily df: precipitation_probability_max and uv_max are null, everything else matches and is the same, remove these two rows

This row is interesting in hourly df: showers 143280.0 0.000000 0.000000 0.000000 0.000000 0.000000 0.000000 0.000000

Daily:

Need to put some of the temperature variables together -> temp max and apparent temp max, temp min and apparent temp min.

- Min and max are heavily correlated, but it still seems the difference would relate to weather anomalies.

Precipitation sum seems it could be determined through rain sum and snow sum.

Drop row candidates:

temperature_2m_min apparent_temperature_min 0.996824 --- drop apparent
temperature_2m_max apparent_temperature_max 0.993810 --- drop apparent
temperature_2m_mean apparent_temperature_max 0.977895 --- drop apparent
temperature_2m_max temperature_2m_mean 0.974702 --- drop mean
temperature_2m_min temperature_2m_mean 0.974529 --- drop mean
temperature_2m_mean apparent_temperature_min 0.969699 --- drop apparent
temperature_2m_min apparent_temperature_max 0.923718 --- drop apparent
apparent_temperature_max apparent_temperature_min 0.920413 --- drop both
temperature_2m_max temperature_2m_min 0.913863 --- drop apparent
apparent_temperature_min 0.906102
wind_speed_10m_max wind_gusts_10m_max 0.877307 --- keep both (gusts are important to anomalies)
precipitation_sum rain_sum 0.854842 --- drop precip sum (implied from rain and snow sum)

Hourly:

Temp and apparent temp, one can be removed unless there is a strong correlation with anomalies.

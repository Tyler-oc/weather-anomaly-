Two types of anomalies:

1. Variation from expectation at that time of the year. For example, an entire hot January would be defined as an anomaly. Or really high winds more than expected. Useful for general strain on systems, climate data, etc.

2. Variation from previous days. A really hot day after a really cold day would flag. Or high winds after low winds. Useful for agriculture, sensors.

For the first type, I can take a z score and flag an anomaly if it is outside of a set number, say 2 standard deviations away from the expected value for that time of the year in that location. This would classify an anomaly. I could then use the data over a longer range leading up to that, say the previous 3 months to predict anomalies with a random forest.

For the second type, I can take a z score over a rolling window of time, very similarly to the first one to classify anomalies. I would then use shorter data, say a week or two to predict anomalies. For example, a big pressure drop might indicate higher winds.

Plan to start with the first type of anomaly:

1. Fetch the data -> fetch.py file that gets data from openmeteo. I want to classify temperature anomalies.

List of hourly variables to keep:

temperature_2m — primary thermal signal
relative_humidity_2m — moisture in air
precipitation — total liquid equivalent
snowfall — separate from rain, different anomaly profile
snow_depth — accumulated, slow-changing, good context signal
windspeed_10m — surface wind
wind_gusts_10m — extreme wind events
wind_direction_10m — directional context
pressure_msl — synoptic weather pattern signal
cloud_cover — sky conditions
visibility — fog, smoke, severe weather indicator
weathercode — WMO categorical code, encodes overall conditions
vapour_pressure_deficit — combines temp and humidity into one stress signal

List of daily variables to keep:

temperature_2m_max — daily peak
temperature_2m_min — daily floor
precipitation_sum — total daily precip
snowfall_sum — total daily snow
windspeed_10m_max — peak wind
windgusts_10m_max — peak gust
precipitation_hours — how long it rained, not just how much
sunshine_duration — clear vs overcast day signal
uv_index_max — solar intensity
weathercode — dominant daily condition

2. Data cleaning and analysis:

First time through this involves looking at covariance matrices, and will use a notebook to do this. After doing this investigation, a pipeline will start to be formed in ingest.py. This will take in the data from fetch.py and craft any variables needed, while removing unimportant variables. After this, there will be a pandas dataframe with data. The next step in ingest.py is anomaly detection. In this, a z-score will be used along each variable to detect an anomaly. This only has to be done once for historic data.

3. Model training:

Build a random forest with the X being the full input, and y being an option between each type of anomaly. This way the model can learn from all of the data and classify as one or more anomalies for a day. Do this with sklearn. Use jobload or something like that to put it into a pkl file. Also save the scaler and feature names in pkl files.

4. Main cron job:

Run weekly / monthly, predict the possibility of an anomaly.

import openmeteo_requests
import requests_cache
import pandas as pd
import argparse
from retry_requests import retry
from sqlalchemy import create_engine

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

def fetch_weather_data(api_url, start_date, end_date, db_params, table_name, latitude=60.1695, longitude=24.9354):
    # Construct API request params
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ["temperature_2m", "rain", "snowfall", "weather_code", "soil_temperature_0_to_7cm", "relative_humidity_2m", "precipitation"],
        "timezone": "Europe/Berlin"
    }

    # Fetch data from Open-Meteo API
    responses = openmeteo.weather_api(api_url, params=params)
    
    # Process the first response
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process hourly data
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_rain = hourly.Variables(1).ValuesAsNumpy()
    hourly_snowfall = hourly.Variables(2).ValuesAsNumpy()
    hourly_weather_code = hourly.Variables(3).ValuesAsNumpy()
    hourly_soil_temperature_0_to_7cm = hourly.Variables(4).ValuesAsNumpy()
    hourly_relative_humidity_2m = hourly.Variables(5).ValuesAsNumpy()
    hourly_precipitation = hourly.Variables(6).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )}

    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["rain"] = hourly_rain
    hourly_data["snowfall"] = hourly_snowfall
    hourly_data["weather_code"] = hourly_weather_code
    hourly_data["soil_temperature_0_to_7cm"] = hourly_soil_temperature_0_to_7cm
    hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
    hourly_data["precipitation"] = hourly_precipitation

    hourly_dataframe = pd.DataFrame(data=hourly_data)
    print(hourly_dataframe)

    # Connect to PostgreSQL and insert data
    engine = create_engine(f'postgresql://{db_params["user"]}:{db_params["password"]}@{db_params["host"]}:{db_params["port"]}/{db_params["db"]}')
    
    hourly_dataframe.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
    print(f"Data successfully inserted into table {table_name}.")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Fetch weather data and insert into PostgreSQL')
    parser.add_argument('--start_date', required=True, help='Start date for weather data')
    parser.add_argument('--end_date', required=True, help='End date for weather data')
    parser.add_argument('--user', required=True, help='PostgreSQL user')
    parser.add_argument('--password', required=True, help='PostgreSQL password')
    parser.add_argument('--host', required=True, help='PostgreSQL host')
    parser.add_argument('--port', required=True, help='PostgreSQL port')
    parser.add_argument('--db', required=True, help='PostgreSQL database name')
    parser.add_argument('--table_name', required=True, help='PostgreSQL table name')
    parser.add_argument('--api_url', required=True, help='API URL for weather data')

    args = parser.parse_args()

    # Prepare DB connection parameters
    db_params = {
        "user": args.user,
        "password": args.password,
        "host": args.host,
        "port": args.port,
        "db": args.db
    }

    # Fetch and insert weather data
    fetch_weather_data(
        api_url=args.api_url,
        start_date=args.start_date,
        end_date=args.end_date,
        db_params=db_params,
        table_name=args.table_name
    )

if __name__ == '__main__':
    main()
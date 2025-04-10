import openmeteo_requests
import requests_cache
import pandas as pd
import argparse
from retry_requests import retry
from google.cloud import bigquery

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

client = bigquery.Client.from_service_account_json("C:/Users/ayhan/.google/my-creds.json")

def fetch_weather_data(api_url, start_date, end_date, project_id, dataset_id, table_name, latitude=60.1695, longitude=24.9354):
    # Construct API request params
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ["temperature_2m", "rain", "snowfall", "weather_code", "soil_temperature_0_to_7cm", "relative_humidity_2m", "precipitation"],
        "timezone": "Europe/Berlin"
    }

    # Fetch data from Open-Meteo archive API
    responses = openmeteo.weather_api(api_url, params=params)
    response = responses[0]
    
    # Process hourly data
    hourly = response.Hourly()
    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )
    }

    # Map variables from API response to dataframe columns
    variables = ["temperature_2m", "rain", "snowfall", "weather_code", "soil_temperature_0_to_7cm", "relative_humidity_2m", "precipitation"]
    for i, var in enumerate(variables):
        hourly_data[var] = hourly.Variables(i).ValuesAsNumpy()
    
    hourly_dataframe = pd.DataFrame(data=hourly_data)
    print(hourly_dataframe.head())
    
    # Upload data to BigQuery
    client = bigquery.Client(project=project_id)
    table_id = f"{project_id}.{dataset_id}.{table_name}"
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    job = client.load_table_from_dataframe(hourly_dataframe, table_id, job_config=job_config)
    job.result()  # Wait for job to complete
    
    print(f"Data successfully inserted into BigQuery table {table_id}.")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Fetch weather data and insert into BigQuery')
    parser.add_argument('--start_date', required=True, help='Start date for weather data')
    parser.add_argument('--end_date', required=True, help='End date for weather data')
    parser.add_argument('--project_id', required=True, help='Google Cloud project ID')
    parser.add_argument('--dataset_id', required=True, help='BigQuery dataset ID')
    parser.add_argument('--table_name', required=True, help='BigQuery table name')
    parser.add_argument('--api_url', required=True, help='API URL for weather data')
    
    args = parser.parse_args()
    
    # Fetch and insert weather data
    fetch_weather_data(
        api_url=args.api_url,
        start_date=args.start_date,
        end_date=args.end_date,
        project_id=args.project_id,
        dataset_id=args.dataset_id,
        table_name=args.table_name
    )

if __name__ == '__main__':
    main()

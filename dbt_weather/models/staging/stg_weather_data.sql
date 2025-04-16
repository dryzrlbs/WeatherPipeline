{{
    config(
        materialized='view'
    )
}}

with weather_data as 
(
  select *,
    row_number() over(partition by date) as rn
  FROM {{ source('weather_data', 'weather_data') }}


  where temperature_2m is not null 
    and temperature_2m between -50 and 50
    and date>='2015-01-01'
)

SELECT
    -- timestamps
    cast(date as timestamp) as date,
    temperature_2m AS temperature,
    rain,
    snowfall,
     -- identifiers
    weather_code,
    relative_humidity_2m AS humidity,
    precipitation
FROM weather_data
where rn=1




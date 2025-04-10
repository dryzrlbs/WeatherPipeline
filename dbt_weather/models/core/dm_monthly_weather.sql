{{ config(materialized='table') }}

with weather_data as (
    select * from {{ ref('fact_weather_data') }}
)
    select 
    -- monthly grouping 
     {{ dbt.date_trunc("month", "date") }} as date_month, 

    -- calculation 
    sum(rain) as total_rain,
    sum(snowfall) as totalsnowfall,

    -- Additional calculations
    max(weather_code) as max_weather_code,
    avg(temperature) as avg_temperature,
    avg(humidity) as avg_humidity

    from weather_data
    group by 1
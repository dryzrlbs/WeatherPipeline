{{
    config(
        materialized='table'
    )
}}

with fact_weather_data as (
    select * FROM  {{ ref('stg_weather_data') }}
),

dim_weather_codes as (
    select * from {{ ref('dim_weather_codes') }}
) 
select *
from fact_weather_data
left join dim_weather_codes as wc
on fact_weather_data.weather_code= wc.code

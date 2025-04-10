{{ config(materialized='table') }}

select 
   *
from {{ ref('weather_codes_lookup') }}
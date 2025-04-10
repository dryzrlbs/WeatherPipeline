
FROM python:3.9.21

RUN apt-get install wget
RUN pip install pandas sqlalchemy psycopg2 requests openmeteo-requests retry-requests requests_cache

WORKDIR /app
COPY weather_ingest.py weather_ingest.py 

ENTRYPOINT [ "python", "weather_ingest.py" ]
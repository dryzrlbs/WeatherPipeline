#FROM kestra/kestra:latest
#COPY ./kestra.yml /app/config/kestra.yml


# Kestra base image
FROM kestra/kestra:latest

# Gerekli sistem paketlerini kur
USER root
RUN apt-get update && \
    apt-get install -y python3-pip && \
    pip3 install --upgrade pip

# dbt ve adapter kur
RUN pip3 install dbt-core dbt-postgres

# protobuf uyumlu sürümünü yükle
RUN pip install "protobuf<6.0,>=5.0"
# dbt ve adapter'ı kur
RUN pip install dbt-core dbt-postgres


# dbt çalışıyor mu test edelim
RUN dbt --version

# Kullanıcıyı tekrar kestra olarak ayarlıyoruz
USER kestra


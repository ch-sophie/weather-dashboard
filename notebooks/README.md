- python3 src/extract_weather.py   
fetches + lands new JSON files for all cities (if add new cities need to rerun everything)
- python3 pipeline/bronze.py            
appends new rows into Bronze
- python3 pipeline/silver.py            
rebuilds Silver from all of Bronze (overwrite)
- python3 pipeline/gold.py               
rebuilds Gold from all of Silver (overwrite)

- airflow with docker
- docker-compose build (build image)
docker-compose up airflow-init
docker-compose up -d
docker-compose ps (check)

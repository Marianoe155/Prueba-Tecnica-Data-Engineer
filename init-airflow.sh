#!/bin/bash
# This script initializes the Airflow database

echo "Initializing Airflow database..."
docker-compose run --rm webserver airflow db init

echo "Creating admin user..."
docker-compose run --rm webserver airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin

echo "Airflow setup completed!"

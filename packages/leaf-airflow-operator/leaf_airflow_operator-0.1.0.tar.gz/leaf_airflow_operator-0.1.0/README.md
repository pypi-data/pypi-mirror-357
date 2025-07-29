# Leaf Airflow Operator

A custom Apache Airflow operator and hook to interact with the Leaf Agriculture API.

## Features
- Satellite field creation
- Field creation
- Batch upload and monitoring

## Usage
```python
from leaf_airflow_operator.operators.leaf_operator import LeafAPIRequestOperator

LeafAPIRequestOperator(
    task_id="get_leaf_fields",
    endpoint="/v1/fields",
    method="GET",
    headers={"Authorization": "Bearer <your_token>"}
)
```

## How to test it locally

### Install Aiflow locally

python -m venv airflow-venv
source airflow-venv/bin/activate

pip install "apache-airflow[celery,postgres,redis]==2.7.3" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.7.3/constraints-3.9.txt"

### Configure Airflow

export AIRFLOW_HOME=~/airflow
airflow db init

airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  --password admin

### Install the example DAG

export AIRFLOW__CORE__DAGS_FOLDER=<PATH TO YOUR DAGS FOLDER>

### Start Airflow

pkill -f airflow

airflow webserver --port 8080 &
airflow scheduler &

### List the DAGs
airflow dags list



# LICENSE (MIT)
MIT License

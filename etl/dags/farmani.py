
import datetime
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
import sys
sys.path.append('..')
from parsers.start import spam


with DAG(
    dag_id='farmani_etl',
    schedule_interval="0 0 * * *",
    start_date=datetime.datetime(2023, 10, 19),
    catchup=False,
    dagrun_timeout=datetime.timedelta(minutes=60),
    tags=["parser"]
) as dag:
    crawler_task = PythonOperator(
        task_id="crawler",
        python_callable=spam,
        dag=dag
    )


crawler_task

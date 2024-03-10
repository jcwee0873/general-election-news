import pendulum
from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta


local_tz = pendulum.timezone("Asia/Seoul")

default_args = {
    'owner': 'jcwee',
    'start_date': datetime(2024, 3, 10, 13, 30, tzinfo=local_tz),
    'retries': 0
}

dag = DAG(
    dag_id='NewsScrapMigrate',
    default_args=default_args,
    schedule_interval='*/10 * * * *',
    tags=['News', 'Scrap', 'Migrate']
)


task1 = BashOperator(
    task_id='NewsScrapMigrate',
    bash_command='/home/jcwee/anaconda3/envs/dev311/bin/python /home/jcwee/Documents/src/general-election-news/app_news_migrate.py',
    dag=dag
)

task1
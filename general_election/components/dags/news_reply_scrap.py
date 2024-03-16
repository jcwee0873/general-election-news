import pendulum
from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta


local_tz = pendulum.timezone("Asia/Seoul")

default_args = {
    'owner': 'jcwee',
    'start_date': datetime(2024, 3, 11, 15, 0, tzinfo=local_tz),
    'retries': 0
}

dag = DAG(
    dag_id='NewsReplyScrap',
    default_args=default_args,
    schedule_interval='0 * * * *',
    tags=['News', 'Reply', 'Scrap']
)


task1 = BashOperator(
    task_id='NewsReplyScrap',
    bash_command='/home/jcwee/anaconda3/envs/dev311/bin/python /home/jcwee/Documents/src/general-election-news/app_news_reply_scrap.py',
    dag=dag
)

task1
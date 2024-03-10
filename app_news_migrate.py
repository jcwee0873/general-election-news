import uuid
from dotenv import load_dotenv
load_dotenv('/home/jcwee/Documents/src/.env')

from general_election.database.database import PostgresqlEngine
from general_election.database.sql import *

DB = PostgresqlEngine()
LAST_RUN_PATH = '/home/jcwee/Documents/src/general-election-news/last_migrate_time.txt'


def load_last_migrate_time():
    try:
        with open(LAST_RUN_PATH, 'r') as f:
            last_migrate_time = f.read()
    except:
        print("Can't find", LAST_RUN_PATH)
        last_migrate_time = '20240101000000'

    return last_migrate_time



def main():
    last_migrate_time = load_last_migrate_time()
    df = DB.read_sql(SELECT_NEWS_MIGRATE_TARGET.format(
        sql_last_run=last_migrate_time
    ), to_df=True)

    print('Migrate', len(df), 'news', 'from', last_migrate_time)

    df['name_id'] = df['pvdr_cd'] + '_' + df['naver_url']
    df['news_id'] = df.name_id.apply(lambda x: uuid.uuid3(uuid.NAMESPACE_DNS, x))

    last_run = None
    for i, row in df.iterrows():
        sql = INSERT_NEWS.format(**row)
        DB.execute(sql)
        last_run = row['published_at']


    with open(LAST_RUN_PATH, 'w') as f:
        f.write(str(last_run))


if __name__ == "__main__":
    main()
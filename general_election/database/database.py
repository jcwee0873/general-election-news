import os
import re
from dotenv import load_dotenv
from opensearchpy import OpenSearch

load_dotenv('/home/jcwee/Documents/src/.env')

import sqlalchemy
import pandas as pd
from urllib.parse import quote
from sqlalchemy import text


URL_PATTERN = re.compile(r'\$\{[^}]*\}')

class PostgresqlEngine:
    def __init__(
        self,
        url: str = "postgresql://${POSTGRESQL_USER}:${POSTGRESQL_PASSWORD}@${POSTGRESQL_HOST}:${POSTGRESQL_PORT}/${POSTGRESQL_DB}"
    ) -> None:
        patterns = URL_PATTERN.findall(url)
        for pattern in patterns:
            url = url.replace(
                pattern,
                quote(os.environ.get(pattern[2:-1]))
            )

        self.engine = sqlalchemy.create_engine(url)


    def read_sql(
        self, sql: str, to_df=False
    ) -> pd.DataFrame | tuple:
        with self.engine.begin() as conn:
            if to_df:
                return pd.read_sql(text(sql), conn)
            
            return conn.execute(text(sql)).fetchall()
        

    def execute(
            self, sql: str
    ) -> None:
        with self.engine.begin() as conn:
            res = conn.execute(text(sql))

            return res
        


class OpenSearchEngine:
    def __init__(self):
        hosts = os.environ.get('OPENSEARCH_HOST').split(',')
        hosts = [{'host': h, 'port': os.environ.get('OPENSEARCH_POSRT')} for h in hosts]

        self.client = OpenSearch(
            hosts=hosts,
            http_auth=(os.environ.get('OPENSEARCH_USER'), os.environ.get('OPENSEARCH_PASSWORD')),
            ssl_assert_hostname=False,
            ssl_show_warn=False,
        )


    
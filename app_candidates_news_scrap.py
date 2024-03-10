import re
import bs4
import ssl
import time
import urllib3
import requests
import pandas as pd

from dotenv import load_dotenv
load_dotenv('/home/jcwee/Documents/src/.env')


from general_election.scraper.parser import TextDensity
from general_election.scraper.scrap import eliminate_something
from general_election.scraper.url_loader import naver_url_load
from general_election.database.database import PostgresqlEngine
from general_election.database.sql import *

DB = PostgresqlEngine()
WWW_COMPILE = re.compile(r'http(s)?://([a-z]+)\.([a-z0-9-]+)\.(co.kr|kr|com|net|[a-z]+)')


class CustomHttpAdapter (requests.adapters.HTTPAdapter):
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_context=self.ssl_context)


def get_legacy_session():
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
    session = requests.session()
    session.mount('https://', CustomHttpAdapter(ctx))
    return session


def load_scrap_target():
    df = DB.read_sql(SELECT_CANDIDATE_SCRAP_TARGET, to_df=True)
    return df


def scrap_news_body(url: str, text_density: bool = False) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Whale/3.20.182.14 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    }
    
    res = get_legacy_session().get(url, headers=headers)
    
    try:
        soup = bs4.BeautifulSoup(res.content.decode('euc-kr'), 'html.parser')
    except:
        soup = bs4.BeautifulSoup(res.content.decode('utf-8'), 'html.parser')
    
    if text_density:
        body = soup.find('body')

        parser = TextDensity(html_tags=body)
        return parser.calc_density(CTD=False, decompose=True)

    body_tag = soup.find('div', {'id': 'newsct_article'})

    return body_tag.text.strip()



def scrap_news(row: dict):
    date = pd.to_datetime(row['pubDate'])

    result = {
        'title': row['title'],
        'origin_url': row['originallink'] if row['originallink'] != '' else row['link'],
        'naver_url': row['link'],
        'summary': row['description'],
        'published_at': date.strftime('%Y%m%d%H%M%S')
    }

    url = result['origin_url']

    pattern = WWW_COMPILE.match(url)
    if not pattern:
        media = url.split('.')[0]
        media = re.sub('http(s)?://', '', media)
    else:
        try:
            if pattern.group(3) == 'co':
                media = url.split('.')[0]
                media = re.sub('http(s)?://', '', media)
            else:
                media = url.split('.')[1]
        except:
            media = url.split('.')[1]

    result['domain_name'] = media

    if 'news.naver' in url:
        time.sleep(0.7)

        text = scrap_news_body(url, text_density=False)
    else:
        text = scrap_news_body(url, text_density=True)

    result['text'] = text

    return {k: eliminate_something(v) for k, v in result.items()}


def insert_data(data: dict):
    try:
        DB.execute(INSERT_NEWS_SCRAP.format(**data))
    except Exception as e:
        print(e)


def scrap_process(row: pd.Series):
    candidate_nm = row['candidate_nm']
    last_dttm = row['last_dttm']

    if pd.isnull(last_dttm):
        last_dttm = None

    news_list = naver_url_load(
        candidate_nm,
        target_date=last_dttm,
        size=1000,
        sort='date'
    )

    print(candidate_nm, ':', len(news_list))

    collect_no = DB.execute(INSERT_NEWS_SCRAP_COLLECT.format(keyword=candidate_nm))
    collect_no = collect_no.fetchone()[0]

    for news in news_list:
        try:
            result = scrap_news(news)
        except Exception as e:
            print(news['title'], e)
            continue

        result['collect_no'] = collect_no

        insert_data(result)


def main():
    scrap_targets = load_scrap_target()

    for idx, row in scrap_targets.iterrows():
        scrap_process(row)


if __name__ == "__main__":
    main()
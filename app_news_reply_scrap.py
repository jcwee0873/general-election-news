from general_election.database.database import PostgresqlEngine
from general_election.scraper.scrap import news_reply_scrap, eliminate_something
from general_election.database.sql import *

DB = PostgresqlEngine()


def main():
    df = DB.read_sql(SELECT_NEWS_REPLY_TARGET, to_df=True)

    print('Reply scrap target:', len(df))

    for row in df.itertuples():
        naver_url = row.naver_url
        rply_url = naver_url.replace('/article/', '/article/comment/')
        rplies = news_reply_scrap(
            rply_url,
            headless=True
        )
        sql = []
        for i, rply in enumerate(rplies):
            rply['rply_no'] = i + 1
            rply['news_id'] = row.news_id

            rply['rply'] = eliminate_something(rply['rply'])
            rply['writer'] = eliminate_something(rply['writer'])

            sql.append(INSERT_NEWS_REPLY_VAL.format(**rply))
            
        if len(sql) > 0:
            sql = INSERT_NEWS_REPLY_COL + ', '.join(sql) + 'ON CONFLICT DO NOTHING;'
            
            DB.execute(sql)

            print(rply['news_id'], len(rplies))
        else:
            rply = {
                'news_id': row.news_id,
                'rply_no': 0,
                'rply': 'NULL',
                'writer': 'NULL',
                'agree_cnt': 0,
                'disagree_cnt': 0,
                'written_at': 'NULL'
            }

            sql = INSERT_NEWS_REPLY_COL + INSERT_NEWS_REPLY_VAL.format(**rply) + 'ON CONFLICT DO NOTHING;'

            DB.execute(sql)

            print(rply['news_id'], 0)


if __name__ == "__main__":
    main()
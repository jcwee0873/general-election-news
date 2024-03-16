import uuid
import time
import threading
import numpy as np
import pandas as pd
from langchain_openai import OpenAIEmbeddings

from langchain.text_splitter import RecursiveCharacterTextSplitter
from general_election.database import PostgresqlEngine, OpenSearchEngine
from general_election.analyzer.chain import count_message_tokens, load_analyze_chain
from general_election.database.sql import *


DB = PostgresqlEngine()
SEARCH = OpenSearchEngine()
EMBEDDINGS = OpenAIEmbeddings(model='text-embedding-3-small')
ANAL_CHAIN = load_analyze_chain()
TEXT_SPLITTER = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=50)


def load_news_data(row: pd.Series):
    target = row['candidate_nm'] + ' ' + row['candidate_title']

    query_dsl = {
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": target,
                            "operator": "and"
                        }
                    },
                    {
                        "range": {
                            "timestamp": {
                                "gte": "2024-02-18"
                            }
                        }
                    }
                ]
            }
        },
        "size": 10000,
        "_source": ["news_id", "text", "timestamp"],
        "track_total_hits": True
    }
    news = SEARCH.client.search(index='news', body=query_dsl)
    news = [d['_source'] for d in news['hits']['hits']]

    return pd.DataFrame(news)


def analyze_news(news: pd.Series):
    text = news['text']
    target = (news['candidate_nm'] + ' ' + news.get('candidate_title', '')).strip()
    
    token_len =  count_message_tokens(text)
    if token_len > 2400:
        texts = TEXT_SPLITTER.split_text(text)
        anal_result = {
            'positive': [],
            'negative': []
        }

        for t in texts:
            tmp_result = ANAL_CHAIN.invoke({
                'target': target,
                'article': t
            })

            tmp_result = {
                'positive': tmp_result.get('positive', 'none'),
                'negative': tmp_result.get('negative', 'none')
            }
            for k, v in tmp_result.items():
                if v == 'none':
                    pass
                else:
                    anal_result[k] = v.split('\n')

        return anal_result


    else:
        anal_result = ANAL_CHAIN.invoke({
            'target': target,
            'article': news['text']
        })

        anal_result = {
            'positive': anal_result.get('positive', 'none'),
            'negative': anal_result.get('negative', 'none')
        }

        for k, v in anal_result.items():
            if v == 'none':
                anal_result[k] = []
            else:
                anal_result[k] = v.split('\n')

        return anal_result


def analyze(row:pd.Series):
    if pd.isnull(row['text']): return

    anal_result = analyze_news(row)
    sentence_list = []

    for k, v in anal_result.items():
        if v:
            for sentence in v:
                vectors = EMBEDDINGS.embed_query(sentence)
                sentence_list.append({
                    'sentence': sentence,
                    'sentiment': k,
                    'vectors': vectors
                })


    insert_data = row[['id', 'news_id', 'timestamp', 'province', 'city', 'district', 'election_dist', 'political_party', 'candidate_nm']].to_dict().copy()
    insert_data['analysis_result'] = sentence_list

    SEARCH.insert_analysis_result(insert_data)

    print(row['candidate_nm'], row['news_id'], 'done:', len(sentence_list))


def make_uuid(row: pd.Series):
    name = '_'.join(row.tolist())
    return uuid.uuid3(uuid.NAMESPACE_DNS, name)


def main():
    # 탈당일 20240218
    df = DB.read_sql(SELECT_CANDIDATE_ANALYZE_TARGET, to_df=True)

    for i, candi in df.iterrows():
        news_list = load_news_data(candi)

        for k, v in candi.items():
            news_list[k] = v
        news_list['id'] = news_list[['province', 'city', 'district', 'election_dist', 'political_party', 'candidate_nm', 'news_id']].apply(make_uuid, axis=1)
        news_list['anal_done'] = news_list['id'].apply(lambda x: SEARCH.client.exists('analyzed_news', id=x))
        news_list = news_list[~news_list.anal_done].reset_index()
        print(candi['candidate_nm'], ':', len(news_list))

        length = len(news_list)
        indices = np.arange(length)
        batch_size = 20
        batchs = np.split(indices, list(range(batch_size, length, batch_size)))
        
        for batch in batchs:
            threads = []
            for i, row in news_list.loc[batch].iterrows():
                thread = threading.Thread(target=analyze, args=(row,))
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

            time.sleep(45)

        






if __name__ == "__main__":
    main()
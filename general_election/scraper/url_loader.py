import os
import json
import requests
import pandas as pd


NAVER_API_URL = "https://openapi.naver.com/v1/search/{div}.json"
KAKAO_API_URL = "https://dapi.kakao.com/v2/search/{div}"

NAVER_HEADERS = {
    "X-Naver-Client-Id": os.environ.get('NAVER_CLIENT_ID'),
    "X-Naver-Client-Secret": os.environ.get('NAVER_CLIENT_SECRET'),
}

KAKAO_HEADERS = {
    'Authorization': "KakaoAK " + os.environ.get('KAKAO_API_KEY')
}

def naver_api_call(keyword, start, display, div='news', sort="date"):
    params = {
        "query": keyword,
        "display": display,
        "start": min(1000, start),
        "sort": sort
    }
    url = NAVER_API_URL.format(div=div)
    res = requests.get(url, params=params, headers=NAVER_HEADERS)

    return json.loads(res.text).get('items', [])


def naver_url_load(keyword, target_date: str | None = None, size=100, div='news', sort="date"):
    """
    Scraping Naver article with Keyword
    > div: (str) Naver scarp Target 'news', 'cafearticle'
    """
    if target_date:
        result = []
        i = 0
        while True:
            res = naver_api_call(
                keyword=keyword, 
                start=(i * 100) + 1, 
                display=100,
                div=div,
                sort=sort
            )

            if res: result += res
            
            if len(result) == 0: break

            if (i * 100) + 1 > 1000:
                break

            last_date = pd.to_datetime(result[-1]['pubDate']).strftime('%Y%m%d%H%M%S') 
            if last_date <= target_date:
                break
            i += 1

        for i in range(len(result)):
            date = pd.to_datetime(result[i]['pubDate']).strftime('%Y%m%d%H%M%S')
            if date <= target_date:
                return result[:i]
                
        return result

    elif size > 100:
        size = min(size, 1000)
        result = []
        for i in range(size // 100):
            result += naver_api_call(
                keyword=keyword, 
                start=(i*100) + 1, 
                display=100,
                div=div,
                sort=sort
            )

        return result
    
    else:
        return naver_api_call(
            keyword=keyword, 
            start=1, 
            display=size,
            div=div,
            sort=sort
        )
    

def kakao_api_call(
    keyword: str,
    page: int = 1,
    size: int = 50,
    div: str = "cafe"
):
    url = KAKAO_API_URL.format(div=div)
    params = {
        "query": keyword,
        "sort": "recency",
        "page": page,
        "size": size,
    }

    res = requests.get(url, params=params, headers=KAKAO_HEADERS)

    return json.loads(res.text).get('documents')
    

def kakao_url_load(
    keyword: str,
    size: int = 50,
    div: str = 'cafe'
):
    page = size // 50 if size > 50 else 1
    residual_size = size % 50 if size > 50 else size
    residual_size = 50 if residual_size == 0 else residual_size

    result = []
    for i in range(1, page+1):
        result += kakao_api_call(
            keyword=keyword,
            page=i,
            size=residual_size if i == page else 50,
            div=div
        )

    
    return result

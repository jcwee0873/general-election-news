import re
import time
import datetime
import pendulum
import pandas as pd
from selenium.webdriver.common.by import By

from .webdriver import CustomWebDriver
from .url_loader import naver_url_load, kakao_url_load

KST = pendulum.timezone("Asia/Seoul")
WWW_COMPILE = re.compile(r'http(s)?://([a-z]+)\.([a-z0-9-]+)\.(co.kr|kr|com|net|[a-z]+)')

RPLY_SELECTOR = {
    "reply": ["span", {"class": "u_cbox_contents"}],
    "writer": ["span", {"class": "u_cbox_nick"}],
    "wrt_dttm": ["span", {"class": "u_cbox_date"}],
    "agr_cnt": ["em", {"class": "u_cbox_cnt_recomm"}],
    "disagr_cnt": ["em", {"class": "u_cbox_cnt_unrecomm"}]
}

def news_reply_scrap(
    rply_url: str,
    headless: bool = False
) -> list[dict]:
    driver = CustomWebDriver(headless=headless)

    driver.get(rply_url)
    time.sleep(8)

    try:
        button = driver.find_element(By.CLASS_NAME, 'u_cbox_btn_more')
    except:
        return []

    while True:
        try:
            button.click()
            time.sleep(3)
        except:
            break

    source = driver.get_page_source()
    rply_list = source.find_all('li', {'class': 'u_cbox_comment'})

    result = []
    for rply_source in rply_list:
        temp = {}
        try:
            for key, value in RPLY_SELECTOR.items():
                temp[key] = rply_source.find(value[0], value[1]).get_text()
            temp['wrt_dttm'] = pd.to_datetime(temp['wrt_dttm']).strftime('%Y%m%d%H%M%S') 
            temp['scrap_dttm'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            result.append(temp)
        except AttributeError:
            continue
    
    return result


def target_range_over(
    sns_date: pd.Timestamp,
    target_date: pd.Timestamp | None = None,
    hours_range: int = 1,
) -> bool:
    if not target_date: False

    diff = (target_date - sns_date).seconds / 60

    if diff <= (60 * hours_range):
        return False
    
    return True


# def community_scrap(
#     target: str,
#     page_size: int = 1,
#     minutes_before: int | None = None,
#     hours_range: int | None = None,
#     headless: bool = False,
#     over_thres: int = 20
# ):
#     driver = CustomWebDriver(headless=headless)
#     parser = CommunityParser()

#     articles = []
#     for i in range(1, page_size + 1):
#         url = parser.board_url(target, page=i)
#         driver.get(url)

#         articles += parser.article_list(
#             driver.get_page_source(),
#             target
#         )

#     logger.info(
#         f"Target: '{target}' /  Article Counts: {len(articles)}"
#     )

#     if minutes_before:
#         target_date = pd.to_datetime(pd.Timestamp.now(tz=KST).strftime('%Y%m%d%H%M%S')) - pd.Timedelta(minutes=minutes_before)
#     else:
#         target_date = None

#     over_cnt = 0
#     result = []
#     for i, article in enumerate(articles):
#         data = {
#             'url': article
#         }

#         driver.get(article)
#         soup = driver.get_page_source()
#         if soup == '': continue

#         body = parser.body(soup, target)
#         if body == '': continue

#         body['wrt_dttm'] = parser.date(body['wrt_dttm'])

#         if target_range_over(
#             body['wrt_dttm'],
#             target_date=target_date,
#             hours_range=hours_range
#         ):
#             if target_date < body['wrt_dttm']: continue

#             over_cnt += 1
#             if over_cnt > over_thres:
#                 break
#             continue

#         comments = parser.comments(soup, target)

#         data.update(body)
#         data.update({'comments': comments})        
#         result.append(data)


#         time.sleep(1)

#     driver._kill_driver()

#     return result


# def naver_cafe_scrap(
#     keyword: str, 
#     size: int = 100,
#     minutes_before: int | None = None,
#     hours_range: int | None = None,
#     headless: bool = False,
#     over_thres: int = 3
# ):
#     driver = ORMASWebDriver(headless=headless)
#     parser = CommunityParser()

#     res = naver_url_load(
#         keyword, 
#         target_date=None, 
#         size=size, 
#         div='cafearticle'
#     )

#     if minutes_before:
#         target_date = pd.to_datetime(pd.Timestamp.now(tz=KST).strftime('%Y%m%d%H%M%S')) - pd.Timedelta(minutes=minutes_before)
#     else:
#         target_date = None

#     over_cnt = 0
#     result = []
    
#     check_url = re.compile('^https?://cafe.naver.com/')

#     for i, row in enumerate(res):
#         cafe_nm = check_url.sub('' , row['link']).split('/')[0]
#         if cafe_nm == 'joonggonara': continue

#         data = {
#             "ttle": row["title"],
#             "url": row["link"]
#         }
#         ok = driver.get(row['link'])
#         time.sleep(1)
#         if not ok: continue

#         driver.switch_to_frame("cafe_main")

#         soup = driver.get_page_source()
#         if soup == '': continue

#         body = parser.body(soup, 'naver_cafe')
#         if body == '': continue
        
#         body['wrt_dttm'] = parser.date(body['wrt_dttm'])

#         if target_range_over(
#             body['wrt_dttm'],
#             target_date=target_date,
#             hours_range=hours_range
#         ):
#             if target_date < body['wrt_dttm']: continue
#             over_cnt += 1
#             if over_cnt > over_thres:
#                 break
#             continue

#         comments = parser.comments(soup, 'naver_cafe')

#         data.update(body)
#         data.update({"comments": comments})

#         result.append(data)

#         logger.info(
#             f"{data['ttle']} ({data['wrt_dttm']}) / {len(data['comments'])}"
#         )

#         time.sleep(0.5)

#     driver._kill_driver()

#     return result


# def kakao_cafe_scrap(
#     keyword: str, 
#     size: int = 100,
#     minutes_before: int | None = None,
#     hours_range: int | None = None,
#     headless: bool = False,
#     over_thres: int = 3
# ):
#     driver = ORMASWebDriver(headless=headless)
#     parser = CommunityParser()

#     res = kakao_url_load(
#         keyword, 
#         size=size, 
#         div='cafe'
#     )

#     if minutes_before:
#         target_date = pd.to_datetime(pd.Timestamp.now(tz=KST).strftime('%Y%m%d%H%M%S')) - pd.Timedelta(minutes=minutes_before)
#     else:
#         target_date = None

#     over_cnt = 0
#     result = []

#     for i, row in enumerate(res):
#         data = {
#             "ttle": row["title"],
#             "url": row["url"]
#         }

#         ok = driver.get(row['url'])
#         time.sleep(1)
#         if not ok: continue

#         driver.switch_to_frame("down")

#         soup = driver.get_page_source()
#         if soup == '': continue

#         body = parser.body(soup, 'kakao_cafe')
#         if body['txt'] == '': continue
        
#         body['wrt_dttm'] = parser.date(body['wrt_dttm'])

#         if target_range_over(
#             body['wrt_dttm'],
#             target_date=target_date,
#             hours_range=hours_range
#         ):
#             if target_date < body['wrt_dttm']: continue

#             over_cnt += 1
#             if over_cnt > over_thres:
#                 break
#             continue

#         comments = parser.comments(soup, 'kakao_cafe')

#         data.update(body)
#         data.update({"comments": comments})

#         logger.info(
#             f"{data['ttle']} ({data['wrt_dttm']}) / {len(data['comments'])}"
#         )

#         result.append(data)
        
#         time.sleep(0.5)

#     driver._kill_driver()

#     return result

import re
import bs4
import copy
import requests
import numpy as np
import pandas as pd 

from .scrap_config import ScrapConfig


# class CommunityParser:
#     def __init__(self):
#         self.config = ScrapConfig()


#     def board_url(self, target: str, page: int = 1):
#         page = 30 * (page - 1) + 1 if target == 'mlbpark' else page
#         url = self.config.config[target].get('board_url').format(page=page)

#         return url


#     def article_list(self, tags: bs4.element.Tag, target: str) -> list:
#         base = self.config.config[target]['list_base']
#         list_tags = tags.find_all("a", self.config.config[target]['list_tag'])
#         urls = [
#             base + tag.get('href', '').replace('amp;', '')
#             for tag in list_tags
#         ]

#         return list(set(urls))
    
#     def decompose_tags(self,
#         tags: bs4.element.Tag,
#         decompose_list: list = [
#             'img'
#         ]
#     ):
#         for decompose_tag in decompose_list:
#             for t in tags.find_all(decompose_tag):
#                 t.decompose()


#     def body(self, tags: bs4.element.Tag, target: str) -> dict:
#         self.decompose_tags(tags)
#         selectors = self.config.config[target].get('body_tag')

#         result = {}
#         for key, selector in selectors.items():
#             result[key] = []

#             for s in selector:
#                 tag, attr = s
#                 result[key] = tags.find_all(tag, attr)
#                 if len(result[key]) > 0: break
            
#             if len(result[key]) > 0:
#                 txt = ''
#                 for t in result[key]:
#                     txt += '\n' + t.text
#                 result[key] = txt.strip()

#             else:
#                 result[key] = ''
        
#         return result


#     def comments(self, tags: bs4.element.Tag, target: str) -> list:
#         self.decompose_tags(tags)
#         selectors = self.config.config[target]['comment_tag']['rply_table']
#         for selector in selectors:
#             if len(selector) == 0: break
                
#             rply_table = tags.find(selector[0], selector[1])
            
#             if rply_table: break

#         if not rply_table: return []

#         list_selectors = self.config.config[target]['comment_tag']['rply_list']
#         rply_selectors = self.config.config[target]['comment_tag']['rply']
#         replies = rply_table.find_all(list_selectors[0], list_selectors[1])

#         comments = []
#         for reply in replies:
#             comment = reply.find_all(rply_selectors[0], rply_selectors[1])
#             for c in comment:
#                 comments.append(c.text.strip())

#         return comments
        

#     def date(self, text: str):
#         form = re.compile('[0-9]{2,4}[\.-]?[0-9]{2}[\.-]?[0-9]{2}[\.]?[\(월화수목금토일\)]{0,3} [0-9].:[0-9].')
#         date = form.findall(text.replace('\xa0', ''))[0]
#         remove_day = re.compile('\([월화수목금토일]\)')
#         date = remove_day.sub('', date)
#         return pd.to_datetime(date)


class TextDensity:
    def __init__(
        self, 
        url: str | None = None, 
        html_tags: bs4.element.Tag | str | None = None,
        length_criterion: str = 'char'
    ):
        """
        > url: (str) URL이 주어질 경우 GET 요청을 통해 Tag 획득
        > html_tags: (bs4.element.Tag | str) HTML TAG가 주어질 경우 바로 사용
        > length_criterion: (str) 'char', 'word' 밀도 계산을 위한 Text 길이 측정 기준
        """
        if html_tags:
            if isinstance(html_tags, bs4.element.Tag):
                self.target = html_tags
            else:
                self.target = bs4.BeautifulSoup(html_tags, 'html.parser')
            
        elif url:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Whale/3.20.182.14 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            }
            res = requests.get(url, headers=headers)
            
            if not res.ok: 
                raise
            try:
                soup = bs4.BeautifulSoup(res.content.decode('euc-kr'), 'html.parser')
            except:
                soup = bs4.BeautifulSoup(res.content.decode('utf-8'), 'html.parser')

            self.target = soup.find('body')
            
        else:
            raise Exception('URL 또는 HTML TAG가 주어져야 합니다.')
            
        self.length_criterion = length_criterion
                
        
    def decompose_tags(self,
        tag,
        decompose_list: list = [
            'script', 'a', 'style', 'button', 'header', 'i', 'noscript', 'figcaption', 
            'dl', 'dt', 'dd', 'ul', 'br', 'option', 'address', 'ins', 'img', 'li', 'legend', 'h2', 'h3', 'use'
        ]
    ):
        for decompose_tag in decompose_list:
            for t in tag.find_all(decompose_tag):
                t.decompose()

        for t in tag.find_all('div', {'id': re.compile('footer[a-z]{0,}')}):
            t.decompose()
            
        for t in tag.find_all('div', {'class': 'inbox'}):
            t.decompose()
        
        
    def _remove_garbage_text(self, text):
        text = re.sub('\s{3,}', '<SPLIT CRITERION>', text).split('<SPLIT CRITERION>')
        text = '\n'.join([t for t in text if len(t.strip()) > 10])
        return text
    
    def _calc_tag_number(self, tag: bs4.element.Tag):            
        return max(1, len(list(tag.children)))
    
    
    def _calc_char_number(self, tag: bs4.element.Tag):
        text = tag.get_text()
        text = self._remove_garbage_text(text)
        
        match self.length_criterion:
            case 'char':
                length = len(text)
            case 'word':
                length = len(text.split())
                
        return length
    
    def _calc_link_char_number(self, tag: bs4.element.Tag):
        total_len = 0
        for t in tag.find_all('a'):
            total_len += self._calc_char_number(t)
        
        return total_len
    
    
    def _calc_link_tag_number(Self, tag: bs4.element.Tag):
        return max(1, len(tag.find_all('a')))
    
    
    def calc_TD_score(self, tag):
        C = self._calc_char_number(tag)
        T = self._calc_tag_number(tag)
        
        return C / T
    
    
    def _calc_CTD_log_part(self, tag, target):
        C = self._calc_char_number(tag)
        T = self._calc_tag_number(tag)
        
        LC = max(1, self._calc_link_char_number(tag))
        LT = max(1, self._calc_link_tag_number(tag))
        
        LCB = self._calc_link_char_number(target)
        CB = self._calc_char_number(target)
        
        bottom = np.log((C/max(1, C-LC))*LC+((LCB/CB)*C+np.e))
        top = (C/LC)*(T/LT)
        
        if top == 0 or bottom == 1 : return 0
        return np.log(top) / np.log(bottom)
    
    def calc_density(self, CTD=False, decompose=False):
        text = ''
        max_score = 0
        max_text = None
        
        target = copy.copy(self.target)
        if decompose:
            self.decompose_tags(target)
        
        for tag in target.find_all():            
            td_score = self.calc_TD_score(tag)
            
            if CTD:
                log_part = self._calc_CTD_log_part(tag, target)
                score = td_score * log_part
            else:
                score = td_score
            
            if score > max_score:
                max_score = score
                text = self._remove_garbage_text(tag.text)
            
        return text
    

import re
import bs4
import copy
import requests
import numpy as np

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
    

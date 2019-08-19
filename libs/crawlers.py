import json
import logging
import random
import time
from pathlib import Path
from urllib import parse

import requests
from bs4 import BeautifulSoup
from user_agent import generate_user_agent

from const import data_dir
from libs.utils import random_throttle
from news import Article


class Crawler:
    def __init__(self):
        self.proxies = self.load_proxy()

    def load_proxy(self, path: Path = data_dir / 'proxies.json') -> list:
        proxies = []
        with open(path) as proxy_file:
            proxies = json.load(proxy_file)
        return proxies

    def get_random_proxy_str(self):
        proxy = self.proxies[random.randint(0, len(self.proxies) - 1)]
        return f'{proxy["ip"]}:{proxy["port"]}'


class GoogleCrawler(Crawler):
    def __init__(self):
        super().__init__()

    @staticmethod
    def is_google_site(url: str):
        hostname = parse.urlparse(url).hostname
        if not hostname:
            return False
        return hostname.endswith('google.com')

    @random_throttle(20)
    def google_search(self, word: str, site: str, offset: int = 0):
        search_url = f'https://www.google.com/search?q={word}+site:{site}{"" if offset == 0 else "&start={offset}"}'
        headers = {'User-Agent': generate_user_agent()}
        proxy = self.get_random_proxy_str()
        res = requests.get(
            search_url,
            headers=headers,
            proxies={
                'http': f'http://{proxy}'
            }
        )
        soup = BeautifulSoup(res.content, 'html.parser')
        links = filter(lambda x: 'href' in x.attrs, soup.find_all('a'))
        links = map(lambda x: x.attrs['href'], links)
        links = filter(lambda x: x.startswith('/url'), links)
        links = map(lambda x: parse.parse_qs(parse.urlparse(x).query)['q'][0], links)
        links = filter(lambda x: not x.startswith('/'), links)
        links = filter(lambda x: not self.is_google_site(x), links)
        links = list(links)

        if not links:
            logging.warning(f'Possible failed: {site} {word}')
            hostname = parse.urlparse(site).hostname
            with open(f'possible_failed/{hostname}_{word}.html', 'w') as out:
                out.write(bytes(str(res.content), 'utf8').decode('unicode_escape'))

        return links

    def get_trending_words(self):
        trending_url = 'https://trends.google.com.tw/trends/api/dailytrends?hl=zh-TW&tz=-480&geo=TW&ns=15'
        res = requests.get(trending_url)
        res = str(res.content).split('\\n')[1].strip('\'')
        raw_trending = json.loads(res, encoding='utf8')
        raw_trending = raw_trending['default']['trendingSearchesDays']

        trending_words = {}
        for searches in raw_trending:
            timestamp = int(time.mktime(time.strptime(searches['date'], '%Y%m%d')))
            for search in searches['trendingSearches']:
                query_string = search['title']['query']
                word = bytes(query_string, 'utf8').decode('unicode_escape')
                trending_words[word] = timestamp
        return trending_words


class NewsCrawler(Crawler):
    def __init__(self):
        super().__init__()

    @random_throttle(10)
    def parse_news_url(self, url: str):
        return Article(url)

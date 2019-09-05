import json
import logging
import os
import random
import time
from pathlib import Path
from typing import Dict
from urllib import parse

import requests
from bs4 import BeautifulSoup
from stem import Signal
from stem.control import Controller
from twnews.soup import NewsSoup
from user_agent import generate_user_agent

from const import data_dir, log_dir
from libs.utils import random_throttle
from models.article import Article
from models.trend import Trend
from models.website import Website


class Crawler:
    def __init__(self):
        self.captcha = 0
        self.proxies = self.load_proxy()

    def load_proxy(self, path: Path = data_dir / 'proxies.json') -> list:
        proxies = []
        with open(path) as proxy_file:
            proxies = json.load(proxy_file)
        return proxies

    def get_random_proxy(self) -> Dict:
        proxy = self.proxies[random.randint(0, len(self.proxies) - 1)]
        return {'http': f'http://{proxy["ip"]}:{proxy["port"]}'}

    def get_tor_proxy(self) -> Dict:
        return {
            'http': 'socks5://localhost:9050',
            'https': 'socks5://localhost:9050'
        }

    def renew_ip(self):
        with Controller.from_port(port=9051) as controller:
            controller.authenticate(os.getenv('TOR_PASSWORD'))
            # pylint: disable=no-member
            controller.signal(Signal.NEWNYM)
            # pylint: enable=no-member


class GoogleCrawler(Crawler):
    def __init__(self):
        super().__init__()

    @staticmethod
    def is_google_site(url: str):
        hostname = parse.urlparse(url).hostname
        if not hostname:
            return False
        return hostname.find('google') != -1

    @random_throttle(60)
    def google_search(self, trend: Trend, site: Website, offset: int = 0) -> list:
        word = trend.keyword.name
        site_url = site.url
        search_url = f'https://www.google.com/search?q={word}+site:{site_url}{"" if offset == 0 else "&start={offset}"}'
        headers = {'User-Agent': generate_user_agent()}
        session = requests.session()
        session.headers = headers
        session.proxies = self.get_random_proxy()
        res = session.get(search_url)
        soup = BeautifulSoup(res.content, 'html.parser')
        links = self.get_links_from_soup(soup)

        if not links:
            logging.warning('Possible failed: %r %r', site_url, word)
            hostname = parse.urlparse(site_url).hostname
            with open(log_dir / f'{hostname}_{word}.html', 'w') as out:
                out.write(bytes(str(res.content), 'utf8').decode('unicode_escape'))
            if self.captcha == 2:
                raise RuntimeError('Stop for captcha')
            self.captcha += 1
            # self.renew_ip()
        else:
            self.captcha = 0

        return links

    def get_links_from_soup(self, soup: BeautifulSoup):
        links = []
        for element in soup.find_all('a'):
            if 'href' not in element.attrs:
                continue
            link = element.attrs['href']
            if link.startswith('/url'):
                try:
                    l = parse.parse_qs(parse.urlparse(link).query)['q'][0]
                except KeyError:
                    l = parse.parse_qs(parse.urlparse(link).query)['url'][0]
                if l.startswith('/'):
                    logging.warning('Parse link failed: %r, after:%r', link, l)
                    continue
                if self.is_google_site(l):
                    continue
                links.append(l)
            elif link.startswith('/search'):
                continue
            elif not self.is_google_site(link):
                if not parse.urlparse(link).netloc:
                    continue
                links.append(link)
        return links

    def get_trending_words(self):
        trend_base_url = 'https://trends.google.com.tw/trends/api/dailytrends?hl=zh-TW&tz=-480&geo=TW&ns=15'
        res = requests.get(trend_base_url)
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
        soup = NewsSoup(url)
        return soup

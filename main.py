import logging
import time
from itertools import zip_longest
from urllib import parse

import pony.orm as orm

from app.controllers.article_controller import ArticleController
from app.controllers.author_controller import AuthorController
from app.controllers.trend_controller import TrendController
from app.controllers.website_controller import WebsiteController
from app.crawlers import GoogleCrawler, NewsCrawler
from models.utils import get_database


def crawl_trends():
    google_crawler = GoogleCrawler()
    trends = google_crawler.get_trending_words()
    trend_controller = TrendController()
    ts = []
    for name, timestamp in trends.items():
        ts.append(trend_controller.insert_or_ignore(name, timestamp))
    return ts

@orm.db_session
def crawl_article_urls():
    trend_controller = TrendController()
    website_controller = WebsiteController()
    article_controller = ArticleController()

    google_crawler = GoogleCrawler()

    trends = trend_controller.get_first(20)
    websites = website_controller.get_websites()

    articles = []
    for trend in trends:
        for website in websites:
            links = google_crawler.google_search(trend, website)
            for link in links:
                article = article_controller.insert_or_ignore(link)
                article.trend = trend
                article.website = website
                logging.info((article.url, trend.keyword.name, website.name))
                orm.commit()
                articles.append(article)
    return articles

def get_pending_articles():
    article_controller = ArticleController()
    website_controller = WebsiteController()

    websites = website_controller.get_websites()
    pending_articles = article_controller.get_pending_articles()
    website_article = {}
    for website in websites:
        website_article[website] = []

    for article in pending_articles:
        website_article[article.website].append(article)

    for articles in zip_longest(*website_article.values()):
        for article in articles:
            if article is None:
                continue
            yield article

@orm.db_session
def crawl_articles():
    news_crawler = NewsCrawler()
    author_controller = AuthorController()
    for article in get_pending_articles():
        soup = news_crawler.parse_news_url(article.url)
        try:
            logging.warning('title: %s, url: %s', soup.title(), article.url)
        except:
            continue
        if soup.title() is None:
            continue
        article.title = soup.title()
        if soup.author():
            author = author_controller.insert_or_ignore(soup.author(), article.website)
            author.website = article.website
            article.author = author
        if not soup.contents() is None:
            article.content = soup.contents()
        if not soup.date() is None:
            article.timestamp = int(soup.date().timestamp())
        orm.commit()


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger("stem").setLevel(logging.ERROR)
    logging.getLogger('twnews').setLevel(logging.ERROR)
    db: orm.Database = get_database()
    db.generate_mapping(create_tables=True)
    
    crawl_trends()
    try:
        crawl_article_urls()
    except Exception as e:
        logging.exception('Exception: %r', e)
    crawl_articles()

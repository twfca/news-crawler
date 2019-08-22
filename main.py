from models.utils import get_database
from app.controllers.website_controller import WebsiteController
from app.controllers.article_controller import ArticleController
from app.controllers.trend_controller import TrendController
from app.crawlers import GoogleCrawler
import logging

import pony.orm as orm

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

    trends = trend_controller.get_first(40)
    websites = website_controller.get_websites()

    articles = []
    for trend in trends:
        for website in websites:
            links = google_crawler.google_search(trend, website)
            for link in links:
                article = article_controller.insert_or_ignore(link)
                article.trend = trend
                article.website = website
                print(article.url, trend.keyword.name, website.name)
                orm.commit()
                articles.append(article)
    return articles

if __name__ == '__main__':
    logging.getLogger("stem").setLevel(logging.ERROR)
    db = get_database()
    db.generate_mapping(create_tables=True)
    articles = crawl_article_urls()
import logging
from typing import List

import pony.orm as orm

from app.controllers.controller import Controller
from models.article import Article


class ArticleController(Controller):
    def __init__(self):
        super().__init__()

    @orm.db_session
    def insert(self, url: str) -> Article:
        return Article(url=url)

    def insert_or_ignore(self, url: str) -> Article:
        article = self.select_by_url(url)
        if article:
            return article
        return self.insert(url)

    @orm.db_session
    def select_by_url(self, url: str) -> Article:
        articles = orm.select(a for a in Article if a.url == url).limit(1)
        if len(articles) == 1:
            return articles[0]

    @orm.db_session
    def get_pending_articles(self):
        return orm.select(
            a for a in Article if a.title is None or len(a.title) == 0
        ).order_by(lambda a: a.website)

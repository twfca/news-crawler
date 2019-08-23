import logging
from typing import List

import pony.orm as orm

from app.controllers.controller import Controller
from app.controllers.keyword_controller import KeywordController
from models.trend import Trend


class TrendController(Controller):
    def __init__(self):
        super().__init__()

    @orm.db_session
    def insert(self, name: str, timestamp: int) -> Trend:
        keyword_controller = KeywordController()
        keyword = keyword_controller.insert_or_ignore(name)
        return Trend(keyword=keyword, timestamp=timestamp)

    def insert_or_ignore(self, name: str, timestamp: int) -> Trend:
        trend = self.select_by_name_and_timestamp(name, timestamp)
        if trend:
            return trend
        return self.insert(name, timestamp)

    @orm.db_session
    def select_by_name_and_timestamp(self, name: str, timestamp: int) -> Trend:
        keyword_controller = KeywordController()
        k = keyword_controller.select_by_name(name)
        if not k:
            return
        trends = orm.select(t for t in Trend if t.keyword == k and t.timestamp == timestamp).limit(1)
        if len(trends) == 1:
            return trends[0]

    @orm.db_session
    def get_first(self, limit: int, offset: int = 0) -> List[Trend]:
        return orm.select(t for t in Trend).order_by(lambda t: orm.desc(t.timestamp)).limit(limit, offset)

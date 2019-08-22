import logging

import pony.orm as orm

from app.controllers.controller import Controller
from models.keyword import Keyword


class KeywordController(Controller):
    def __init__(self):
        super().__init__()

    @orm.db_session
    def insert(self, name: str) -> Keyword:
        return Keyword(name=name)

    def insert_or_ignore(self, name:str) -> Keyword:
        keyword = self.select_by_name(name)
        if keyword:
            return keyword
        return self.insert(name)

    @orm.db_session
    def select_by_name(self, name: str) -> Keyword:
        keywords = orm.select(k for k in Keyword if k.name == name).limit(1)
        if len(keywords) == 1:
            return keywords[0]

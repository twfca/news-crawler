import json
import logging
from pathlib import Path
from typing import List

import pony.orm as orm

from app.controllers.controller import Controller
from models.website import Website


class WebsiteController(Controller):
    def __init__(self):
        super().__init__()

    @orm.db_session
    def insert(self, name: str, url: str) -> Website:
        return Website(name=name, url=url)

    def insert_or_ignore(self, name: str, url: str) -> Website:
        website = self.select_by_name(name)
        if website:
            return website
        return self.insert(name, url)

    @orm.db_session
    def select_by_name(self, name: str) -> Website:
        websites = orm.select(w for w in Website if w.name == name).limit(1)
        if len(websites) == 1:
            return websites[0]

    @orm.db_session
    def get_websites(self) -> List[Website]:
        return orm.select(w for w in Website).fetch()

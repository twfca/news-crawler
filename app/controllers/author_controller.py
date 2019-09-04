import logging

import pony.orm as orm

from app.controllers.controller import Controller
from models.author import Author
from models.website import Website


class AuthorController(Controller):
    def __init__(self):
        super().__init__()

    @orm.db_session
    def insert(self, name: str) -> Author:
        return Author(name=name)

    def insert_or_ignore(self, name:str, site: Website) -> Author:
        author = self.select_by_name_and_site(name, site)
        if author:
            return author
        return self.insert(name)

    @orm.db_session
    def select_by_name_and_site(self, name: str, site: Website) -> Author:
        authors = orm.select(a for a in Author if a.name == name and a.website == site).limit(1)
        if len(authors) == 1:
            return authors[0]

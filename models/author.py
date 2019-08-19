import pony.orm as orm

from models.utils import get_database
from models.website import Website

db = get_database()

class Author(db.Entity):
    _table_ = 'authors'
    id = orm.PrimaryKey(int, auto=True)
    name = orm.Optional(str, unique=True)
    website = orm.Optional(Website)
    articles = orm.Set('Article')
    orm.composite_key(name, website)

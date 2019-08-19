import pony.orm as orm

from models.author import Author
from models.trend import Trend
from models.website import Website
from models.utils import get_database

db = get_database()

class Article(db.Entity):
    _table_ = 'articles'
    id = orm.PrimaryKey(int, auto=True)
    title = orm.Optional(str)
    url = orm.Required(str, unique=True)
    content = orm.Optional(str)
    author = orm.Optional(Author)
    website = orm.Optional(Website)
    trend = orm.Optional(Trend)
    timestamp = orm.Optional(int)

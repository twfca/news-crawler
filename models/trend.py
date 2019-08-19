import pony.orm as orm

from models.keyword import Keyword
from models.utils import get_database

db = get_database()

class Trend(db.Entity):
    _table_ = 'trends'
    id = orm.PrimaryKey(int, auto=True)
    keyword = orm.Optional(Keyword)
    timestamp = orm.Optional(int)
    articles = orm.Set('Article')
    orm.composite_key(keyword, timestamp)

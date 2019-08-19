import pony.orm as orm

from models.utils import get_database

db = get_database()

class Keyword(db.Entity):
    _table_ = 'keywords'
    id = orm.PrimaryKey(int, auto=True)
    name = orm.Required(str, unique=True)
    trends = orm.Set('Trend')

import pony.orm as orm

from models.utils import get_database

db = get_database()

class Website(db.Entity):
    _table_ = 'websites'
    id = orm.PrimaryKey(int, auto=True)
    name = orm.Required(str, unique=True)
    authors = orm.Set('Author')
    articles = orm.Set('Article')

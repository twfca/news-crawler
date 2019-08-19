from libs.utils import cache
from pony.orm import Database
from const import data_dir

@cache
def get_database() -> Database:
    return Database('sqlite', data_dir / 'news.db')
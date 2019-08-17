import json
from crawler import Crawler
import sqlite3

def load_websites(f: str = 'websites.json'):
    with open(f) as websites_file:
        websites = json.load(websites_file)
    return websites

def insert_links_to_db(links: list):
    # pylint: disable=no-member
    conn = sqlite3.connect('news.db')
    # pylint: enable=no-member
    conn.execute('create table if not exists articles (\
        url text primary key,\
        title text,\
        content text\
        )')

    for link in links:
        conn.execute('insert or ignore into articles (url) values (?)', (link,))
    conn.commit()
    conn.close()

def get_target_links(websites: dict):
    c = Crawler()
    words = c.get_trending_words()
    links = []
    for site in websites:
        for word in words:
            ls = c.google_search(word, site['url'])
            insert_links_to_db(ls)
            links = links + ls
    return links

links = get_target_links(load_websites())
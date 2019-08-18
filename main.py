import json
from crawlers import GoogleCrawler, NewsCrawler
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
        url TEXT primary key,\
        title TEXT,\
        content TEXT,\
        author TEXT,\
        date INTEGER\
        )')

    for link in links:
        conn.execute('insert or ignore into articles (url) values (?)', (link,))
    conn.commit()
    conn.close()

def get_target_links(websites: dict):
    c = GoogleCrawler()
    words = c.get_trending_words()
    links = []
    for word in words:
        for site in websites:
            ls = c.google_search(word, site['url'])
            insert_links_to_db(ls)
            links = links + ls
    return links

def get_pending_targets():
    # pylint: disable=no-member
    conn = sqlite3.connect('news.db')
    # pylint: enable=no-member

    result = conn.execute(f'select * from articles where title is NULL')
    urls = result.fetchall()
    urls = map(lambda url: url[0], urls)

    nc = NewsCrawler()
    for url in urls:
        news = nc.parse_news_url(url)
        if not news.title:
            continue
        params = (news.title, news.content, news.author, news.date, url)
        conn.execute(f'update articles\
            set title = ?,\
                content = ?,\
                author = ?,\
                date = ?\
            where url = ?',
        params)
        conn.commit()


if __name__ == '__main__':
    get_pending_targets()
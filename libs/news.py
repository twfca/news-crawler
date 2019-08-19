from twnews.soup import NewsSoup


class Article:
    def __init__(self, url: str, nsoup: NewsSoup = None):
        if nsoup is None:
            nsoup = NewsSoup(url)
        self.title = nsoup.title()
        self.site = nsoup.channel
        self.author = nsoup.author()
        self.content = nsoup.contents()
        if nsoup.date():
            self.date = int(nsoup.date().timestamp())
        else:
            self.date = None
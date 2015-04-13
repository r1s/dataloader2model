import feedparser

from dataloader2model.providers.base import BaseProvider


class RssProvider(BaseProvider):
    
    def __init__(self, url):
        super(RssProvider, self).__init__()
        self.url=url
    
    def get_data(self):
        parser = feedparser.parse(self.url)
        return parser

from dateutil import parser as date_parser

def convert_date(val):
    return date_parser.parse(val)
convert_date.model_attr = 'rss.NewsItem.date'

SCHEMA = \
{'summary_detail':
     {'base': '',
      'type': '',
      'value': '',
      'language': ''},
 'published_parsed': '',
 'links': [{'href': 'rss.NewsItem.source_link', 'type': '', 'rel': ''}],
 'title': 'rss.NewsItem.title',
 'summary': '',
 'guidislink': '',
 'title_detail': {'base': '',
                  'type': '',
                  'value': 'rss.NewsItem.content',
                  'language': ''},
 'link': '',
 'published': convert_date,
 'id': ''}

import os
from django.conf import settings
from django.core.management import BaseCommand
from dataloader2model.mapper.data_mapper import SchemaVisit
from dataloader2model.providers.rss import RssProvider
from dataloader2model.mapper.schema_loader import Schema
from rss.models import NewsItem


class Command(BaseCommand):
    help = '''
    Command for test dataloader2model.
    '''

    def handle(self, *args, **options):
        schema_path = os.path.join(settings.SCHEMES_DIR, 'afisha_gorod.py')
        schema = Schema(schema_path).load()
        data = RssProvider('http://gorod.afisha.ru/export/rss/').get_data()

        print('Objects were: {}'.format(NewsItem.objects.count()))

        sv = SchemaVisit(schema.SCHEMA)
        for entry in data['entries']:
            sv.construct_model(entry)
            sv.storage.save()

        print('Objects was now: {}'.format(NewsItem.objects.count()))
        print("Done!")

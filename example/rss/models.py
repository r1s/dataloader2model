from django.db import models

# Create your models here.


class NewsProvider(models.Model):
    pass


class NewsItem(models.Model):
    title = models.CharField(max_length=1024)
    date = models.DateTimeField()
    content = models.TextField()
    source_link = models.CharField(max_length=2048)

    class Meta:
        app_label = 'rss'


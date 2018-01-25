from django.db import models
from django_resized import ResizedImageField
from model_utils.models import TimeStampedModel


class News(TimeStampedModel):
    name = models.CharField(verbose_name='Name', blank=False, max_length=100)
    content = models.TextField(verbose_name='Content', blank=False)
    pub_date = models.DateTimeField('date published')
    creator = models.CharField(verbose_name='Creator', blank=False, max_length=100)
    image = ResizedImageField(size=[130, 200], crop=['middle', 'center'], verbose_name="Image")

    def __str__(self):
        return '%s' % self.name

    class Meta:
        permissions = (
            ('manage_news', 'Manage_News'),
        )

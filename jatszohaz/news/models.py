from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django_resized import ResizedImageField
from model_utils.models import TimeStampedModel
from jatszohaz.models import JhUser


class News(TimeStampedModel):
    title = models.CharField(verbose_name=_('Title'), max_length=100)
    content = models.TextField(verbose_name=_('Content'))
    creator = models.ForeignKey(JhUser, on_delete=models.PROTECT, verbose_name=_('Creator'))
    image = ResizedImageField(
        size=[500, 500],
        crop=['middle', 'center'],
        verbose_name=_("Image"),
        blank=True,
        null=True
    )
    published = models.BooleanField(
        verbose_name=_("Published"),
        help_text=_("Determines whether everyone sees the post. False: only admins."),
        default=False
    )

    def get_absolute_url(self):
        return reverse_lazy('news:edit', kwargs={'pk': self.pk})

    def __str__(self):
        return "%s %s" % (self.title, self.created)

    class Meta:
        permissions = (
            ('manage_news', 'Manage_News'),
        )

import logging
from django.conf import settings
from django.contrib.auth import user_logged_in
from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.dispatch import receiver
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

logger = logging.getLogger(__name__)


class JhUser(AbstractUser):
    """Custom user model which extends the one provided by Django."""

    mobile = models.CharField(
        verbose_name=_('mobile'),
        max_length=100,
        help_text=_('Mobile number for helping communication if necessary.'),
        blank=True
    )
    room = models.CharField(
        verbose_name=_('room'),
        max_length=100,
        help_text=_('Room number.'),
        blank=True
    )
    checked_profile = models.BooleanField(
        verbose_name=_("Checked profile"),
        help_text=_("From time to time everyone is required to check his profile."),
        default=False
    )

    class Meta:
        permissions = (
            ('view_all', _('View all user details')),
            ('basic_admin', _('Basic admin rights')),
            ('view_user_stat', _('View statistics for users')),
            ('leader_admin', _('Group leader rights')),
        )
        ordering = ('last_name', 'first_name', )

    def get_entitlements(self):
        """
        Gets all auth.sch group memberships.
        Map keys:
         - title (list): all titles in VIR
         - status (str): öregtag tag or körvezető
         - start (date): join date
         - end (date): leave date
        :return: data map of the specified group.
        """
        if self.has_social_auth() and self.social_auth.first().extra_data['eduPersonEntitlement']:
            for i in self.social_auth.first().extra_data['eduPersonEntitlement']:
                if i['id'] == settings.EDU_PERSON_ENTITLEMENT_ID:
                    return i
        return None

    def has_social_auth(self):
        return self.social_auth.count() > 0

    @receiver(user_logged_in)
    def user_logged_in(sender, user, request, **kwargs):
        """
        Runs every time the user logs in.
        """
        user.update_permissions()

    def update_permissions(self):
        """
        Update user rights according to its entitlements
        """
        entls = self.get_entitlements()
        if entls:
            if entls.get('status') in settings.EDU_PERSON_ENTITLEMENT_IGNORE_STATUS:
                logger.warning("Permission update for user with pk %d aborted, because has '%s' status." % (
                    self.pk, entls.get('status')))
                return

            group, created = Group.objects.get_or_create(name='kortag')
            group.user_set.add(self)
            logger.info("Updated permissions for user with pk %d." % self.pk)

    def full_name(self):
        """
        :return: First name + lLst name
        """
        return "%s %s" % (self.first_name, self.last_name)

    def full_name2(self):
        """
        :return: Last name + First name
        """
        return "%s %s" % (self.last_name, self.first_name)

    def get_absolute_url(self):
        """
        Returns the url for this user's profile.
        """
        return reverse_lazy('profile', kwargs={'pk': self.pk})

    def __str__(self):
        return "%s - %s" % (self.full_name2(), self.email)

    @staticmethod
    def reset_all_checked_profile():
        logger.info("Clearing all user's room data and resetting checked_profile flag.")

        for user in JhUser.objects.all():
            user.room = ""
            user.checked_profile = False
            user.save()


class UserComment(TimeStampedModel):
    """Represents a comment for a user object made by a member (who is also a user but with permissions)."""
    user = models.ForeignKey(JhUser, on_delete=models.PROTECT, related_name='user')
    creator = models.ForeignKey(JhUser, on_delete=models.PROTECT, related_name="creator")
    message = models.TextField(verbose_name=_("Message"))


from datetime import datetime

from django.db import connection
from django.db import models
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify


GOOGLE_PROFILE_URL = 'http://www.google.com/s2/favicons?domain_url=%s'
SN_CACHE_KEY = 'elsewhere_sn_data'
IM_CACHE_KEY = 'elsewhere_im_data'


class Network(models.Model):
    """ 
    Model for storing networks. 
    """
    class Meta:
        abstract = True

    name = models.CharField(max_length=100)
    url = models.URLField(verify_exists=False)
    identifier = models.CharField(max_length=100)
    icon = models.CharField(max_length=100, blank=True)

    def __unicode__(self):
        return self.name

class SocialNetwork(Network):
    class Meta:
        verbose_name_plural = 'social networks'

    def save(self, *args, **kwargs):
        cache.delete(SN_CACHE_KEY)
        super(SocialNetwork, self).save(*args, **kwargs)

class InstantMessenger(Network):
    class Meta:
        verbose_name_plural = 'instant messanger networks'

    def save(self, *args, **kwargs):
        cache.delete(IM_CACHE_KEY)
        super(InstantMessenger, self).save(*args, **kwargs)

# the following makes the social / IM networks data act as lists.

def SocialNetworkData():
    cache_key = SN_CACHE_KEY
    data = cache.get(cache_key)

    if not data:
        data = []
        seen_model = connection.introspection.installed_models(['elsewhere_socialnetwork'])

        if seen_model:
            for network in SocialNetwork.objects.all():
                data.append({
                    'id': slugify(network.name),
                    'name': network.name,
                    'url': network.url,
                    'identifier': network.identifier,
                    'icon': network.icon
                })
            cache.set(cache_key, data, 60*60*24)

    return data

def InstantMessengerData():
    cache_key = IM_CACHE_KEY
    data = cache.get(cache_key)
    seen_model = connection.introspection.installed_models(['elsewhere_instantmessenger'])
    
    if seen_model:
        data = []
        for network in InstantMessenger.objects.all():
            data.append({
                'id': slugify(network.name),
                'name': network.name,
                'url': network.url,
                'icon': network.icon
            })
        cache.set(cache_key, data, 60*60*24)

    return data

class ProfileManager:
    """
    Handle raw data for lists of profiles.
    """
    data = {}

    def _get_choices(self):
        """
        List of choices for profile select fields. 
        """
        # following line throws TypeError: 'NoneType' object is not iterable
        # return [(props['id'], props['name']) for props in self.data]
        # dirty fix so syncdb completes
        return None
    choices = property(_get_choices)

class SocialNetworkManager(ProfileManager):
    data = SocialNetworkData()

sn_manager = SocialNetworkManager()

class InstantMessengerManager(ProfileManager):
    data = InstantMessengerData()

im_manager = InstantMessengerManager()

class Profile(models.Model):
    """
    Common profile model pieces. 
    """
    data_manager = None

    class Meta:
        abstract = True

    date_added = models.DateTimeField(_('date added'), auto_now_add=True)
    date_verified = models.DateTimeField(_('date verified'), default=datetime.now)
    is_verified = models.BooleanField(default=False)

    def _get_data_item(self):
        # Find profile data for this profile id
        for network in self.data_manager.data:
            if network['id'] == self.network_id:
                return network
        return None
    data_item = property(_get_data_item)

    def _get_name(self):
        # Profile display name
        return self.data_item['name']
    name = property(_get_name)
 
    def _get_url(self):
        # Profile URL with username
        return self.data_item['url'] % self.username
    url = property(_get_url)
    
    def _get_icon_name(self):
        # Icon name
        return self.data_item['icon']
    icon_name = property(_get_icon_name)
 
    def _get_icon(self):
        # Icon URL or link to Google icon service
        if self.icon_name:
            print reverse('elsewhere_img', args=[self.icon_name])
            print self.icon_name
            return reverse('elsewhere_img', args=[self.icon_name])
        return GOOGLE_PROFILE_URL % self.url
    icon = property(_get_icon)

class SocialNetworkProfile(Profile):
    data_manager = sn_manager

    content_type = models.ForeignKey(ContentType, related_name='social_network_profiles')
    object_id = models.PositiveIntegerField(db_index=True)
    object = generic.GenericForeignKey('content_type', 'object_id')

    network_id = models.CharField(max_length=16, choices=data_manager.choices, db_index=True)
    username = models.CharField(max_length=64)
    
    def __unicode__(self):
        return self.network_id


class InstantMessengerProfile(Profile):
    data_manager = im_manager

    content_type = models.ForeignKey(ContentType, related_name='instant_messenger_profiles')
    object_id = models.PositiveIntegerField(db_index=True)
    object = generic.GenericForeignKey('content_type', 'object_id')

    network_id = models.CharField(max_length=16, choices=data_manager.choices, db_index=True)
    username = models.CharField(max_length=64)

    def __unicode__(self):
        return self.username


class WebsiteProfile(models.Model):
    content_type = models.ForeignKey(ContentType, related_name='website_profiles')
    object_id = models.PositiveIntegerField(db_index=True)
    object = generic.GenericForeignKey('content_type', 'object_id')

    name = models.CharField(max_length=64)
    url = models.URLField(verify_exists=True)

    def __unicode__(self):
        return self.url

    @property
    def icon(self):
        # No known icons! Just return the Google service URL.
        return GOOGLE_PROFILE_URL % self.url

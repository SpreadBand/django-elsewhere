from django.contrib import admin

from models import SocialNetwork
from models import SocialNetworkProfile, WebsiteProfile, InstantMessengerProfile

class ProfileAdmin(admin.ModelAdmin):
    pass

class SocialNetworkProfileAdmin(ProfileAdmin):
    list_display = ('content_type', 'object', 'network', 'username') #, 'date_added')

class InstantMessengerProfileAdmin(ProfileAdmin):
    list_display = ('content_type', 'object', 'network', 'username') #, 'date_added')

class WebsiteProfileAdmin(ProfileAdmin):
    list_display = ('content_type', 'object', 'name', 'url') #, 'date_added')

## TODO Not sure why I can't grab date_added from the parent Profile model, need to figure this out.

admin.site.register(SocialNetwork)
admin.site.register(SocialNetworkProfile, SocialNetworkProfileAdmin)
admin.site.register(WebsiteProfile, WebsiteProfileAdmin)
admin.site.register(InstantMessengerProfile, InstantMessengerProfileAdmin)

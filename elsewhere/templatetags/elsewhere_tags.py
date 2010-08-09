from django import template

from elsewhere.models import SocialNetworkProfile, InstantMessengerProfile

register = template.Library()

class BaseForObjectNode(template.Node):
    """
    An base class for getting profiles related to an object
    """
    def __init__(self, obj, context_var):
        self.obj = template.Variable(obj)
        self.context_var = context_var

    def _get_context(self, context):
        return NotImplemented

    def render(self, context):
        context[self.context_var] = self._get_context(context)
        return ''

class SocialNetworkProfilesForObjectNode(BaseForObjectNode):
    def _get_context(self, context):
        return SocialNetworkProfile.objects.get_for_object(self.obj.resolve(context))

class InstantMessengerProfilesForObjectNode(BaseForObjectNode):
    def _get_context(self, context):
        return InstantMessengerProfile.get_for_object(self.obj.resolve(context))

class WebsiteProfileForObjectNode(BaseForObjectNode):
    def _get_context(self, user):
        return user.website_profiles.all()


def do_socialnetworks_for_object(parser, token):
    """
    Retrieves a list of ``SocialNetworkProfile`` objects associated with 
    a given object and stores them in a context variable.

    Usage::

       {% elsewhere_networks [object] as [varname] %}

    Examples::

       {% elsewhere_networks request.user as user_networks %}

    """
    try:
        tag_name, obj, as_string, context_var = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly three arguments" % token.contents.split()[0]
    return SocialNetworkProfilesForObjectNode(obj, context_var)


def do_elsewhere_messengers(parser, token):
    """
    Retrieves a list of ``InstantMessengerProfile`` objects associated with 
    a given object and stores them in a context variable.

    Usage::

       {% elsewhere_messengers [object] as [varname] %}

    Examples::

       {% elsewhere_messengers request.user as user_messengers %}

    """
    try:
        tag_name, user, as_string, result_var = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly three arguments" % token.contents.split()[0]
    return ElsewhereMessengers(user, result_var)

def do_elsewhere_websites(parser, token):
    """
    Retrieves a list of ``WebsiteProfile`` objects associated with 
    a given user and stores them in a context variable.

    Usage::

       {% elsewhere_websites [user] as [varname] %}

    Examples::

       {% elsewhere_websites request.user as user_websites %}

    """
    try:
        tag_name, user, as_string, result_var = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly three arguments" % token.contents.split()[0]
    return ElsewhereWebsites(user, result_var)

register.tag('socialnetworks_for_object', do_socialnetworks_for_object)
register.tag('elsewhere_messengers', do_elsewhere_messengers)
register.tag('elsewhere_websites', do_elsewhere_websites)







# restaurant/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Returns the value for the key from a dictionary."""
    try:
        return dictionary.get(key)
    except (TypeError, AttributeError):
        return None

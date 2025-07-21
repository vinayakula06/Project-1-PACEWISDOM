# core/templatetags/custom_filters.py
from django import template
register = template.Library()
@register.filter
def replace(value, arg):
    if isinstance(value, str) and isinstance(arg, str) and ',' in arg:
        old, new = arg.split(',', 1) 
        return value.replace(old, new)
    return value

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter(name='add_class')
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg})

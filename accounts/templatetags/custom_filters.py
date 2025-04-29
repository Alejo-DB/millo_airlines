from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def truncate_chars(value, max_length):
    """Truncates text to a maximum length, adding ellipsis if needed."""
    if len(value) > max_length:
        return value[:max_length] + '...'
    return value

@register.filter
def get_item(dictionary, key):
    """Gets a value from a dictionary by its key."""
    return dictionary.get(key)

@register.filter
def currency(value):
    """Formats a value as currency."""
    try:
        value = float(value)
        return f"${value:,.2f}"
    except (ValueError, TypeError):
        return value

@register.filter(name='multiply')
def multiply(value, arg):
    """Multiplies the value by the argument"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return '' 
from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    """Multiplies a value by the argument."""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def split_list(value, arg):
    """Returns an item from a comma-separated list based on the index."""
    try:
        return value.split(',')[int(arg)]
    except (IndexError, ValueError, AttributeError):
        return ''

@register.filter
def subtract(value, arg):
    """Subtracts the argument from the value."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return value 
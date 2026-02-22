from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(str(key))
    if isinstance(dictionary, list):
        try:
            return dictionary[int(key)]
        except (IndexError, ValueError):
            return None
    return None

@register.filter
def abs_val(value):
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return value

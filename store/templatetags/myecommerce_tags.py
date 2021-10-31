from django import template
from store.helpers import rupiah_formatting

register = template.Library()


@register.filter(is_safe=True)
def rupiah_formatting_filter(value):
    return rupiah_formatting(value)

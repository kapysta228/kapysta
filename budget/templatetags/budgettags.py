from django import template

from ..forms import OperationForm

register = template.Library()


@register.simple_tag(name='form')
def form_finance(*args):
    form = OperationForm()
    return form

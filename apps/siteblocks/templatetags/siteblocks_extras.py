# -*- coding: utf-8 -*-
from apps.siteblocks.models import Settings, Banner
from django import template

register = template.Library()

#@register.inclusion_tag("siteblocks/block_setting.html")
#def block_static(name):
#    try:
#        setting = Settings.objects.get(name = name)
#    except Settings.DoesNotExist:
#        setting = False
#    return {'block': block,}

@register.inclusion_tag("siteblocks/block_banner.html")
def block_banner():
    try:
        banner = Banner.objects.published()
        banner = banner.order_by("?")[:1]
    except Settings.DoesNotExist:
        banner = False
    return {'banner': banner,}

@register.filter
def get_range( value ):
  """
    Filter - returns a list containing range made from given value
    Usage (in template):

    <ul>{% for i in 3|get_range %}
      <li>{{ i }}. Do something</li>
    {% endfor %}</ul>

    Results with the HTML:
    <ul>
      <li>0. Do something</li>
      <li>1. Do something</li>
      <li>2. Do something</li>
    </ul>

    Instead of 3 one may use the variable set in the views
  """
  return range( value )

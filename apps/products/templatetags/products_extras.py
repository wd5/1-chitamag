# -*- coding: utf-8 -*-
from django import template
from django.db.models import Q
from apps.products.models import Category
from apps.pages.models import Page
from apps.utils.utils import url_spliter

register = template.Library()

@register.simple_tag
def get_request_parameters(GET_PARAMS, empty_href, excl_param):
    str = ''
    for parameter in GET_PARAMS:
        if excl_param!=parameter:
            str = '%s&%s=%s' % (str, parameter, GET_PARAMS[parameter])

    if str.startswith('&') and empty_href=='True':
        str = '?%s' % str[1:]
    if not str.startswith('?') and empty_href=='True':
        str = '?%s' % str
    if str=='?':
        str = '#'
    return str


@register.inclusion_tag("products/block_catalog_menu.html")
def block_catalog_menu(id_cat):
    menu = Category.objects.filter(is_published=True, parent=None)
    try:
        current = Category.objects.get(is_published=True, id=id_cat)
    except:
        current = False
    if current:
        if current.parent:
            parent_id = current.parent.id
            child_id = current.id
        else:
            parent_id = current.id
            child_id = False
    else:
        parent_id = False
        child_id = False

    return {'menu': menu, 'parent_id': parent_id, 'child_id':child_id }

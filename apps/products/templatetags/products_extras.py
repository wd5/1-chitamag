# -*- coding: utf-8 -*-
from django import template
from apps.products.models import Category

register = template.Library()

@register.simple_tag
def get_request_parameters(GET_PARAMS, empty_href, excl_param):
    str = ''
    excl_params = excl_param.split(',')
    for parameter in GET_PARAMS:
        exclude = False
        for item in excl_params:
            if item == parameter:
                exclude = True
        if not exclude:
            str = '%s&%s=%s' % (str, parameter, GET_PARAMS[parameter])

    if str.startswith('&') and empty_href == 'True':
        str = '?%s' % str[1:]
    if not str.startswith('?') and empty_href == 'True':
        str = '?%s' % str
    if str == '?':
        str = '#'
    return str

@register.simple_tag
def get_unfilter_text(GET_PARAMS, selected_filter_parameters):
    str = u'Вы применили фильтр по '
    array = []
    for parameter in GET_PARAMS:
        if parameter == 'price_filter':
            array.append(u'«Цена»')
        if parameter == 'ship_filter':
            array.append(u'«Срок поставки»')
        if parameter == 'mfr':
            array.append(u'«Производители»')
    if selected_filter_parameters!='':
        for parameter in selected_filter_parameters:
            array.append(u'«%s»' % parameter.title)
    return str + u', '.join(array)


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

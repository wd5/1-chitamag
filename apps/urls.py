# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth import views as auth_views
from django.views.decorators.csrf import csrf_exempt
from apps.products.views import show_category, show_product, actions_list, show_action, load_catalog, search_products, actions_list_archive, load_features_names
from apps.users.views import show_cabinet, edt_profile_info, show_profile_form, registration_form
from apps.users.views import items_loader
from apps.orders.views import check_oneclick_form

from apps.products.management.commands.checkgoods import TestView

from views import index

#url(r'^captcha/', include('captcha.urls')),

urlpatterns = patterns('',
    url(r'^$',index, name='index'),
    (r'^test_load/$',TestView.as_view()),
    (r'^load_items/$',csrf_exempt(items_loader)),
    (r'^load_features_names/$',csrf_exempt(load_features_names)),
    (r'^check_oneclick_form/$',csrf_exempt(check_oneclick_form)),
    (r'^catalog/search/$',search_products,),
    url(r'^catalog/$', index, name='show_catalog'),
    url(r'^catalog/(?P<slug>[^/]+)/$',show_category, {'sub_slug':'all'}, name='show_category' ),
    url(r'^catalog/(?P<slug>[^/]+)/(?P<sub_slug>[^/]+)/$',show_category, name='show_sub_category'),
    url(r'^catalog/(?P<slug>[^/]+)/(?P<sub_slug>[^/]+)/(?P<pk>[^/]+)/$',show_product, name='show_product'),
    (r'^load_catalog/$',load_catalog),

    (r'^actions/$',actions_list),
    (r'^actions/archive/$',actions_list_archive, {'archive':True}),
    (r'^actions/(?P<pk>[^/]+)/$', show_action),

    #url(r'^faq/', include('apps.faq.urls')),

    url(r'^cabinet/$',show_cabinet, name='show_cabinet'),
    (r'^cabinet/edit_info_form/$',show_profile_form),
    (r'^edt_profile_info/$',edt_profile_info),
    (r'^registration_form/$',registration_form),
    url(r'^password/reset/$',
        auth_views.password_reset,
            {'template_name': 'users/password_reset_form.html',},
        name='auth_password_reset'),
    url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm,
            {'template_name': 'users/password_reset_confirm.html'},
        name='auth_password_reset_confirm'),
    url(r'^password/reset/complete/$',
        auth_views.password_reset_complete,
            {'template_name': 'users/password_reset_complete.html'},
        name='auth_password_reset_complete'),
    url(r'^password/reset/done/$',
        auth_views.password_reset_done,
            {'template_name': 'users/password_reset_done.html'},
        name='auth_password_reset_done'),
    url(r'^password/change/$',
        auth_views.password_change,
            {'template_name': 'users/password_change_form.html'},
        name='auth_password_change'),
    url(r'^password/change/done/$',
        auth_views.password_change_done,
            {'template_name': 'users/password_change_done.html'},
        name='auth_password_change_done'),

    url(r'^cart/$','apps.orders.views.view_cart',name='cart'),
    (r'^add_product_to_cart/$','apps.orders.views.add_product_to_cart'),
    (r'^delete_product_from_cart/$','apps.orders.views.delete_product_from_cart'),
    (r'^restore_product_to_cart/$','apps.orders.views.restore_product_to_cart'),
    (r'^change_cart_product_count/$','apps.orders.views.change_cart_product_count'),
    (r'^change_cart_product_service/$','apps.orders.views.change_cart_product_service'),
    (r'^change_cart_product_service_count/$','apps.orders.views.change_cart_product_service_count'),
    (r'^show_order_form/$','apps.orders.views.show_order_form'),
    (r'^order_form_step2/$','apps.orders.views.show_finish_form'),
)




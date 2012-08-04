# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe
from apps.orders.models import Cart,CartProduct,Order,OrderProduct, OneClickBye, CartProductService, OrderProductService

class CartProductInlines(admin.TabularInline):
    model = CartProduct
    readonly_fields = ('product',)
    extra = 0

class CartAdmin(admin.ModelAdmin):
    list_display = ('id','create_date','sessionid',)
    list_display_links = ('id','create_date','sessionid',)
    list_filter = ('create_date',)
    inlines = [CartProductInlines]

class CartProductServiceAdmin(admin.ModelAdmin):
    list_display = ('id','service','count','cart_product',)
    list_display_links = ('id','service','count','cart_product',)
    readonly_fields = ('service','count','cart_product',)

class OrderProductInlines(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('product','count',)
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','create_date','fullname','admin_summary',)
    list_display_links = ('id','fullname','create_date',)
    search_fields = ('fullname','contact_info',)
    list_filter = ('create_date',)
    readonly_fields = ('create_date',)
    inlines = [OrderProductInlines]

class OrderProductServiceAdmin(admin.ModelAdmin):
    list_display = ('id','service','count','order_product',)
    list_display_links = ('id','service','count','order_product',)
    readonly_fields = ('service','count','order_product',)

class ProductLink(forms.TextInput):

    def __int__(self, attrs={}):
        self.attrs = attrs
        if attrs:
            self.attrs.update(attrs)
            super(ProductLink, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = []
        if value==None:
            output.append((u'Товар был удалён из базы данных'))
        else:
            output.append((u'<a target="_blank" href="/admin/products/product/%s/">Ссылка на товар №%s</a><br/><br/>' % (value,value)))
        output.append(super(ProductLink, self).render(name, value, attrs))
        return mark_safe(u''.join(output))

class OneClickByeAdminForm(forms.ModelForm):
    product = forms.CharField(widget=ProductLink({'style':'display:none;'}), label=u'Товар', required=False)

    class Meta:
        model = OneClickBye

class OneClickByeAdmin(admin.ModelAdmin):
    list_display = ('id','phone','create_date',)
    list_display_links = ('id','phone','create_date',)
    list_filter = ('create_date','product')
    form = OneClickByeAdminForm
    #readonly_fields = ('product',)

admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(CartProductService, CartProductServiceAdmin)
admin.site.register(OrderProductService, OrderProductServiceAdmin)
admin.site.register(OneClickBye, OneClickByeAdmin)

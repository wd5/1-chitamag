# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms
from apps.utils.widgets import Redactor
from sorl.thumbnail.admin import AdminImageMixin
from mptt.admin import MPTTModelAdmin
#from apps.utils.customfilterspec import CustomFilterSpec

from models import *

class FeatureNameCategoryAdmin(admin.ModelAdmin):
    list_display = ('id','feature_group','title','in_filter','order','is_published',)
    list_display_links = ('id','feature_group','title',)
    list_editable = ('in_filter','order','is_published',)
    list_filter = ('feature_group','in_filter','is_published')
    search_fields = ('title',)
    #form = ActionAdminForm

admin.site.register(FeatureNameCategory, FeatureNameCategoryAdmin)

class FeatureGroupInline(admin.TabularInline):
    model = FeatureGroup

class FeatureValueInline(admin.TabularInline):
    model = FeatureValue
    extra = 1

class CategoryAdminForm(forms.ModelForm):
    parent = forms.ModelChoiceField(queryset=Category.objects.filter(parent=None), label='Родительская Категория', required=False)

    class Meta:
        model = Category

    class Media:
        js = (
            '/media/js/jquery.js',
            '/media/js/clientadmin.js',
            '/media/js/jquery.synctranslit.js',
            )

class CategoryAdmin(MPTTModelAdmin):
    list_display = ('id','category_name','slug','order','is_published',)
    list_display_links = ('id','category_name',)
    list_editable = ('slug','order','is_published',)
    list_filter = ('is_published',)
    form = CategoryAdminForm
    exclude = ('xml_id','xml_up_id',)
    inlines = [FeatureGroupInline,]
    #custom_filter_spec = {'parent': Category.objects.filter(parent=None)}

admin.site.register(Category, CategoryAdmin)

class ProductImageInline(AdminImageMixin, admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductPropertyInline(AdminImageMixin, admin.TabularInline):
    model = ProductProperty
    extra = 1

#--Виджеты jquery Редактора
class ProductAdminForm(forms.ModelForm):
    #category = forms.ModelChoiceField(queryset=Category.objects.exclude(parent=None), label='Категория', required=True)
    category = forms.ModelChoiceField(queryset=Category.objects.filter(is_published=True), label='Категория', required=True)

    class Meta:
        model = Product

    class Media:
        js = (
            '/media/js/jquery.js',
            '/media/js/load_feature_names.js',
            )

#--Виджеты jquery Редактора
class ProductAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ('id','title','category','price', 'order','is_published',)
    list_display_links = ('id','title','category',)
    list_editable = ('order','is_published','price',)
    list_filter = ('is_published','category','manufacturer',)
    search_fields = ('title', 'price','xml_code',)
#    filter_horizontal = ('related_products',)
    raw_id_fields = ('related_products',)
    readonly_fields = ('xml_code',)
    inlines = [ProductImageInline, ProductPropertyInline, FeatureValueInline, ]
    form = ProductAdminForm
    #custom_filter_spec = {'category': Category.objects.exclude(parent=None)}


admin.site.register(Product, ProductAdmin)


class ActionAdminForm(forms.ModelForm):
    description = forms.CharField(widget=Redactor(attrs={'cols': 110, 'rows': 20}), label='Описание')

    class Meta:
        model = Action

class ActionAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ('id','title','in_archive','order','is_published',)
    list_display_links = ('id','title',)
    list_editable = ('order','in_archive','is_published',)
    search_fields = ('title', 'short_description', 'description',)
    form = ActionAdminForm

admin.site.register(Action, ActionAdmin)

class CategoryServiceAdminForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.exclude(parent=None), label='Категория', required=True)

    class Meta:
        model = CategoryService

class CategoryServiceAdmin(admin.ModelAdmin):
    list_display = ('id','category','short_description','price',)
    list_display_links = ('id','category','short_description',)
    list_editable = ('price',)
    list_filter = ('price','category',)
    form = CategoryServiceAdminForm
    #custom_filter_spec = {'category': Category.objects.exclude(parent=None)}


admin.site.register(CategoryService, CategoryServiceAdmin)

class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('id','title','order','is_published',)
    list_display_links = ('id','title',)
    list_editable = ('order','is_published',)

admin.site.register(Manufacturer, ManufacturerAdmin)

#class PhraseAdmin(admin.ModelAdmin):
#    list_display = ('id','example',)
#    list_display_links = ('id','example',)
#    search_fields = ('example',)
#
#admin.site.register(Phrase, PhraseAdmin)
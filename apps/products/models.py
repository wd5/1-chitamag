# -*- coding: utf-8 -*-
import os, datetime
from django.utils.translation import ugettext_lazy as _
from django.db import models
from apps.utils.managers import PublishedManager

from pytils.translit import translify
from django.core.urlresolvers import reverse

from sorl.thumbnail import ImageField
from mptt.models import MPTTModel, TreeForeignKey, TreeManager

def str_price(price):
    if not price:
        return u'0'
    value = u'%s' %price
    if price._isinteger():
        value = u'%s' %value[:len(value)-3]
        count = 3
    else:
        count = 6

    if len(value)>count:
        ends = value[len(value)-count:]
        starts = value[:len(value)-count]

        return u'%s %s' %(starts, ends)
    else:
        return value

def smart_truncate(content, length=100, suffix='...'):
    if len(content) <= length:
        return content
    else:
        return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix

def file_path_Product(instance, filename):
    return os.path.join('images','products',  translify(filename).replace(' ', '_') )

def file_path_Product(instance, filename):
    return os.path.join('images','products',  translify(filename).replace(' ', '_') )

def file_path_Action(instance, filename):
    return os.path.join('images','actions',  translify(filename).replace(' ', '_') )

class Category(MPTTModel):
    title = models.CharField(verbose_name=u'название', max_length=100)
    title_singular = models.CharField(verbose_name=u'название в единственном числе', help_text=u'например если категория называется "Пылесосы", то название будет "пылесос" ', max_length=100, blank=True)
    slug = models.SlugField(verbose_name=u'Алиас', help_text=u'уникальное имя на латинице',)
    parent = TreeForeignKey('self', verbose_name=u'Родительская категория', related_name='children', blank=True, null=True, on_delete=models.SET_NULL)
    order = models.IntegerField(verbose_name=u'Порядок сортировки',default=10)
    is_published = models.BooleanField(verbose_name = u'Опубликовано', default=True)
    # XML
    xml_id = models.IntegerField(verbose_name=u'id из файла xml', blank=True, null=True)
    xml_up_id= models.IntegerField(verbose_name=u'up_id из файла xml', blank=True, null=True)

    parent.custom_filter_spec = True
    # Managers
    objects = TreeManager()

    def __unicode__(self):
        if self.parent:
            return u'%s - %s' % (self.parent, self.title)
        else:
            return u'%s' % self.title

    class Meta:
        verbose_name =_(u'category')
        verbose_name_plural =_(u'categories')

    class MPTTMeta:
        order_insertion_by = ['order']

    def get_absolute_url(self):
        if self.parent:
            parent_slug = self.parent.slug
            return reverse('show_sub_category',kwargs={'slug': '%s'%parent_slug, 'sub_slug': '%s'%self.slug})
        else:
            return reverse('show_category',kwargs={'slug': '%s'%self.slug})

    def get_services(self):
        return self.categoryservice_set.all()

    def get_products(self):
        products_ids = []
        if self.parent == None:
            products = Product.objects.published()
            for child in self.get_children():
                for product in child.product_set.published():
                    products_ids.append(product.id)
            products = products.filter(id__in=products_ids)
            return products
        else:
            return self.product_set.published()

    def get_feature_names(self):
        name_set = FeatureNameCategory.objects.published().filter(feature_group__category__id=self.id)
        return name_set

    def get_all_feature_groups(self):
        return self.featuregroup_set.published()

    def get_other_feature_groups(self):
        base_group = self.featuregroup_set.published().latest()
        groups = self.featuregroup_set.published().exclude(id=base_group.id)
        return groups

    def get_base_feature_group(self):
        return self.featuregroup_set.published().latest()

class Manufacturer(models.Model):
    title = models.CharField(verbose_name=u'название', max_length=400)
    order = models.IntegerField(verbose_name=u'Порядок сортировки',default=10)
    is_published = models.BooleanField(verbose_name = u'Опубликовано', default=True)

    # Managers
    objects = PublishedManager()

    class Meta:
        ordering = ['-order',]
        verbose_name =_(u'manufacturer')
        verbose_name_plural =_(u'manufacturers')

    def __unicode__(self):
        return self.title

class CategoryService(models.Model):
    category = models.ForeignKey(Category, verbose_name=u'Категория',)
    description = models.TextField(verbose_name=u'описание',)
    price = models.DecimalField(verbose_name=u'Цена', decimal_places=2, max_digits=10,)

    category.custom_filter_spec = True

    class Meta:
        ordering = ['price',]
        verbose_name =_(u'category_service')
        verbose_name_plural =_(u'category_services')

    def __unicode__(self):
        return self.description

    def short_description(self):
        return '<span>%s</span>' % smart_truncate(self.description, 50)

    def get_str_price(self):
        return str_price(self.price)

    short_description.allow_tags = True
    short_description.short_description = 'Краткое описание'

#status_choices = (
#    (u'in_stock',u'есть в наличии'),
#    (u'on_request',u'под заказ'),
#    )

class Product(models.Model):
    category = models.ForeignKey(Category, verbose_name=u'Категория', blank=True, null=True)
    manufacturer = models.ForeignKey(Manufacturer, verbose_name=u'производитель', blank=True, null=True)
    title = models.CharField(verbose_name=u'название', max_length=400)
    image = ImageField(verbose_name=u'изображение', upload_to=file_path_Product)
    description = models.TextField(blank=True, verbose_name=u'описание')
    price = models.DecimalField(verbose_name=u'Цена', decimal_places=2, max_digits=10,)
    price_old = models.DecimalField(verbose_name=u'старая цена', decimal_places=2, max_digits=10, blank=True, null=True)

    status = models.IntegerField(verbose_name=u'Срок поставки в днях', blank=True, null=True) # срок поставки в днях

    is_hit = models.BooleanField(verbose_name = u'Хит', default=False)
    is_new = models.BooleanField(verbose_name = u'Новинка', default=False)
    is_discount = models.BooleanField(verbose_name = u'Скидка', default=False)
    in_slider = models.BooleanField(verbose_name = u'отображать в слайдере на главной', default=False)

    related_products = models.ManyToManyField("self", verbose_name=u'Похожие товары', blank=True, null=True,)

    order = models.IntegerField(verbose_name=u'Порядок сортировки',default=10)
    is_published = models.BooleanField(verbose_name = u'Опубликовано', default=True)

    # XML
    xml_code = models.IntegerField(verbose_name=u'code из файла xml', blank=True, null=True)

    # Дата изменения
    change_date = models.DateTimeField(verbose_name=u'Дата изменения', default=datetime.datetime.now, blank=True, null=True)

    category.custom_filter_spec = True

    # Managers
    objects = PublishedManager()

    class Meta:
        ordering = ['-order',]
        verbose_name =_(u'product_item')
        verbose_name_plural =_(u'product_items')
        get_latest_by = 'change_date'

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('show_product',kwargs={'pk': '%s'%self.id,'slug':'%s'%self.category.parent.slug,'sub_slug':'%s'%self.category.slug})

    def get_str_price(self):
        return str_price(self.price)

    def get_str_price_old(self):
        return str_price(self.price_old)

    def get_related_products(self):
        return self.related_products.published()

    def get_photos(self):
        return self.productimage_set.all()

    def get_properties(self):
        return self.productproperty_set.published()

    def get_feature_values(self):
        return self.featurevalue_set.all()

    def get_base_feature_values(self):
        base_feature_group = self.category.get_base_feature_group()
        base_features = self.get_feature_values().filter(feature_name__feature_group__id=base_feature_group.id)[:6] # только первые 6 характеристик для отображения на главной
        return base_features

class ProductImage(models.Model):
    product = models.ForeignKey(Product, verbose_name=u'Товар')
    image = ImageField(verbose_name=u'Картинка', upload_to=file_path_Product)
    order = models.IntegerField(verbose_name=u'Порядок сортировки',default=10)

    class Meta:
        ordering = ['-order',]
        verbose_name =_(u'product_photo')
        verbose_name_plural =_(u'product_photos')

    def __unicode__(self):
        return u'изображение товара %s' %self.product.title

class ProductProperty(models.Model):
    product = models.ForeignKey(Product, verbose_name=u'Товар')
    value = models.CharField(verbose_name=u'значение', max_length=255)
    order = models.IntegerField(verbose_name=u'Порядок сортировки',default=10)
    is_published = models.BooleanField(verbose_name = u'Опубликовано', default=True)

    # Managers
    objects = PublishedManager()

    class Meta:
        ordering = ['-order',]
        verbose_name =_(u'property')
        verbose_name_plural =_(u'properties')

    def __unicode__(self):
        return self.value


class FeatureGroup(models.Model):
    category = models.ForeignKey(Category, verbose_name=u'Категория',) # todo: только второго уровня
    title = models.CharField(verbose_name=u'название', max_length=400)
    order = models.IntegerField(verbose_name=u'Порядок сортировки',default=10)
    is_published = models.BooleanField(verbose_name = u'Опубликовано', default=True)

    # Managers
    objects = PublishedManager()

    class Meta:
        ordering = ['-order',]
        get_latest_by = 'order'
        verbose_name =_(u'featuregroup_item')
        verbose_name_plural =_(u'featuregroup_items')

    def __unicode__(self):
        return u'%s - %s' % (self.category.title, self.title)

    def get_feature_names(self):
        return self.featurenamecategory_set.published()

class FeatureNameCategory(models.Model):
    feature_group = models.ForeignKey(FeatureGroup, verbose_name=u'Группа',) # todo: только для группы из своей категории
    title = models.CharField(verbose_name=u'название', max_length=400)
    in_filter = models.BooleanField(verbose_name = u'применять при фильтрации', default=False)
    order = models.IntegerField(verbose_name=u'Порядок сортировки',default=10)
    is_published = models.BooleanField(verbose_name = u'Опубликовано', default=True)

    # Managers
    objects = PublishedManager()

    class Meta:
        ordering = ['-order',]
        verbose_name =_(u'featurename_item')
        verbose_name_plural =_(u'featurename_items')

    def __unicode__(self):
        return u'%s - %s' % (self.feature_group, self.title)

class FeatureValue(models.Model):
    product = models.ForeignKey(Product, verbose_name=u'Товар')
    feature_name = models.ForeignKey(FeatureNameCategory, verbose_name=u'название характеристики',)
    value = models.CharField(verbose_name=u'значение', max_length=100)

    class Meta:
        verbose_name =_(u'featurevalue_item')
        verbose_name_plural =_(u'featurevalue_items')

    def __unicode__(self):
        return self.value


class Action(models.Model):
    #product = models.ForeignKey(Product, verbose_name=u'Товар', blank=True, null=True)
    title = models.CharField(verbose_name=u'название', max_length=255)
    image = ImageField(verbose_name=u'Картинка', upload_to=file_path_Action, blank=True)
    short_description = models.TextField(verbose_name=u'краткое описание',)
    description = models.TextField(verbose_name=u'описание',)
    in_archive = models.BooleanField(verbose_name = u'В архив', default=False)
    order = models.IntegerField(verbose_name=u'Порядок сортировки',default=10)
    is_published = models.BooleanField(verbose_name = u'Опубликовано', default=True)

    # Managers
    objects = PublishedManager()

    class Meta:
        verbose_name =_(u'action')
        verbose_name_plural =_(u'actions')
        ordering = ['-order',]

    def __unicode__(self):
        return self.title

#Класс фраз для поиска
#class Phrase(models.Model):
#    example = models.CharField(verbose_name=u'Пример фразы', max_length=100)
#
#    class Meta:
#        verbose_name =_(u'phrase')
#        verbose_name_plural =_(u'phrases')
#
#    def __unicode__(self):
#        return self.example

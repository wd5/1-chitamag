# -*- coding: utf-8 -*-
import datetime
from decimal import Decimal
from django.views.generic.base import TemplateView

__author__ = 'yzero'
from django.core.management.base import BaseCommand
from apps.products.models import Product, Category
from django.core.files.temp import NamedTemporaryFile
from urllib2 import urlopen
from django.core.files import File
import urllib, os, settings
from xml.dom.minidom import *
from apps.products.models import ProductImage, ProductProperty, FeatureValue, FeatureNameCategory, FeatureGroup

# в терминале /home/yzero/projects/chitamag/manage.py checkgoods

class Command(BaseCommand):
    def handle(self, *args, **options):
        return start_parse()


class TestView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(TestView, self).get_context_data(**kwargs)
        context['parse_info'] = start_parse()
        return context


def start_parse():
    try:
        last_change_date = Product.objects.latest().change_date
    except:
        last_change_date = False
    if last_change_date:
        added = 0
        updated = 0

        str = u'%s' % last_change_date
        str = str.replace(':', '').replace('-', '').replace(' ', '')[:-2]

        # сохраним файл по ссылке
        link = "http://ontpay.info/te/test/goodsinc.xsql?timestamp=%s" % str
        file_save_dir = settings.MEDIA_ROOT + '/uploads/'
        filename = 'xml_tmp'
        full_path = os.path.join(file_save_dir, filename + '.xml')
        urllib.urlretrieve(link, full_path)

        all_products = Product.objects.all()
        all_categories = Category.objects.all()
        f = parse(full_path)
        rows_array = f.getElementsByTagName('ROW')
        if rows_array:
            for z in rows_array:
                if z.getAttribute('price'): # парсим товар
                    parsed = 'product'
                    product_title = z.getAttribute('name')
                    product_xml_code = z.getAttribute('code')
                    product_ship = z.getAttribute('ship')
                    product_price = Decimal(z.getAttribute('price'))
                    try:
                        product_old_price = Decimal(z.getAttribute('old_price'))
                    except:
                        product_old_price = False
                    product_change_time = z.getAttribute('timestamp')
                    try:
                        product_description = z.getElementsByTagName('description')[0].firstChild.nodeValue
                    except:
                        product_description = u''
                    grp_id = z.getAttribute('grp_id')
                    try:
                        grp_id = int(grp_id)
                    except:
                        grp_id = 0
                        #superprice = z.getAttribute('superprice')
                    #discountmax = z.getAttribute('discountmax')
                    #action = z.getAttribute('action')

                    try:
                        exits_prod = all_products.get(xml_code=product_xml_code)
                    except:
                        exits_prod = False

                    try:
                        product_ship = int(product_ship)
                    except:
                        product_ship = 0

                    if product_change_time:
                        try:
                            year = int(product_change_time[:4])
                            month = int(product_change_time[4:6])
                            day = int(product_change_time[6:8])
                            hours = int(product_change_time[8:10])
                            minutes = int(product_change_time[10:12])
                            product_change_time = datetime.datetime(year, month, day, hours, minutes, 00)
                        except:
                            product_change_time = None
                    else:
                        product_change_time = None

                    try:
                        prod_category = all_categories.get(xml_id=grp_id)
                        category_feature_names = prod_category.get_feature_names()
                    except:
                        prod_category = False
                        category_feature_names = False

                    new_product = False
                    if not exits_prod: # если продукта с таким же xml_code не существует, то создаём продукт
                        if prod_category:
                            new_product = Product(category=prod_category, title=product_title,
                                description=product_description, status=product_ship,
                                price=product_price, xml_code=product_xml_code, change_date=product_change_time)
                        else:
                            category_feature_names = False
                            new_product = Product(title=product_title, description=product_description,
                                price=product_price, status=product_ship, xml_code=product_xml_code,
                                change_date=product_change_time)
                        if product_old_price:
                            new_product.price_old = product_old_price

                        # добавим данные об типе предложения
                        flag_array = z.getElementsByTagName('flag')
                        if flag_array:
                            for flag in flag_array:
                                flag_name = flag.getAttribute('name')
                                if flag_name == 'superprice':
                                    new_product.is_discount = True
                                elif flag_name == 'hit':
                                    new_product.is_hit = True
                                elif flag_name == 'new':
                                    new_product.is_new = True

                        new_product.save()
                        added += 1
                    else: # если продукт уже есть - смотрим изменения и изменяем
                        exits_prod.change_date = product_change_time
                        if exits_prod.title != product_title:
                            exits_prod.title = product_title
                        if exits_prod.description != product_description:
                            exits_prod.description = product_description
                        if exits_prod.price != product_price:
                            exits_prod.price = product_price
                        if exits_prod.status != product_ship:
                            exits_prod.status = product_ship
                        #проверим изменились ли свойства
                        property_array = z.getElementsByTagName('property')
                        product_properties = exits_prod.get_properties()
                        if property_array:
                            saved_properties = []
                            saved_properties_ids = []
                            for property in property_array:
                                property_value = property.firstChild.nodeValue
                                for property in product_properties:
                                    if property.value == property_value:
                                        saved_properties.append(property.value)
                                        saved_properties_ids.append(property.id)
                            if not saved_properties_ids: # если нет совпадений со свойствами которые уже есть у товара - то удаляем эти свойства
                                for property in product_properties:
                                    property.delete()
                            else: # проверяем какие свойства остались - убираем те, которые не вошли в импорт
                                delete_prod_prop = product_properties.exclude(id__in=saved_properties_ids)
                                for property in delete_prod_prop:
                                    property.delete()

                            for property in property_array:
                                property_value = property.firstChild.nodeValue
                                if property_value not in saved_properties: # если свойства нет в сохраненых свойствах - создаём новые
                                    new_property = ProductProperty(product=exits_prod, value=property_value)
                                    new_property.save()

                        #проверим изменились ли изображения
                        img_array = z.getElementsByTagName('img')
                        exist_product_photos = exits_prod.get_photos()
                        if img_array:
                            for img in img_array:
                                img_link = img.firstChild.nodeValue
                                img_is_default = img.getAttribute('default')
                                if img_is_default == 'yes' and img_link != '': # сохраняем как главное изображение товара
                                    if exits_prod.image:
                                        # удалим основное изображение
                                        try:
                                            os.remove(settings.MEDIA_ROOT + '/%s' % exits_prod.image)
                                            exits_prod.image = ''
                                        except OSError:
                                            pass
                                            # Save image
                                    img_temp = NamedTemporaryFile(delete=True)
                                    try:
                                        img_temp.write(urlopen(img_link).read())
                                        img_temp.flush()
                                        exits_prod.image.save(u"product_image_%s" % exits_prod.id,
                                            File(img_temp))
                                        exits_prod.save()
                                    except:
                                        pass
                                elif img_link != '':
                                    # удалим все дополнительные изображения
                                    if exist_product_photos:
                                        for img in exist_product_photos:
                                            try:
                                                os.remove(settings.MEDIA_ROOT + '/%s' % img.image)
                                                img.delete()
                                            except OSError:
                                                pass
                                            exist_product_photos = []
                                    img_temp = NamedTemporaryFile(delete=True)
                                    try:
                                        img_temp.write(urlopen(img_link).read())
                                        img_temp.flush()
                                        new_image = ProductImage(product=exits_prod)
                                        new_image.image.save(
                                            u"product_image_%s-additional" % exits_prod.pk,
                                            File(img_temp))
                                        new_image.save()
                                    except:
                                        pass

                        #проверим изменилась ли категория
                        parameter_array = z.getElementsByTagName('parameter')
                        product_features = exits_prod.get_feature_values()
                        if exits_prod.category == None or exits_prod.category.xml_id != grp_id:
                            if prod_category: # если категория с таким идентификатором есть - то
                                exits_prod.category = prod_category
                                # удалин значения параметров товара
                                for values in exits_prod.get_feature_values():
                                    values.delete()
                                if parameter_array and prod_category: # если в xml есть теги parameter и определена категория товара
                                    for parameter in parameter_array:
                                        parameter_name = parameter.getAttribute('name')
                                        parameter_name_grp_title = parameter.getAttribute('paramgrp')
                                        parameter_value = parameter.getAttribute('value')
                                        if parameter_name != '' and parameter_value != '' and parameter_name_grp_title != '': # создаём значения параметров
                                            try:
                                                parameter_model_object = category_feature_names.get(
                                                    feature_group__title__exact=parameter_name_grp_title,
                                                    title=parameter_name)
                                            except:
                                                #parameter_model_object = False
                                                if prod_category:
                                                    new_param_group = FeatureGroup(category=prod_category,
                                                        title=parameter_name_grp_title)
                                                    new_param_group.save()
                                                    parameter_model_object = FeatureNameCategory(
                                                        feature_group=new_param_group, title=parameter_name)
                                                    parameter_model_object.save()
                                                else:
                                                    parameter_model_object = False
                                            if parameter_model_object:
                                                new_parameter_value = FeatureValue(product=exits_prod,
                                                    feature_name=parameter_model_object, value=parameter_value)
                                                new_parameter_value.save()
                        else: #проверим обновим параметры
                            if parameter_array and prod_category: # если в xml есть теги parameter и определена категория товара
                                saved_features = []
                                saved_features_ids = []
                                for parameter in parameter_array:
                                    parameter_name = parameter.getAttribute('name')
                                    parameter_name_grp_title = parameter.getAttribute('paramgrp')
                                    parameter_value = parameter.getAttribute('value')
                                    if parameter_name != '' and parameter_value != '' and parameter_name_grp_title != '': # создаём значения параметров
                                        try:
                                            parameter_model_object = category_feature_names.get(
                                                feature_group__title__exact=parameter_name_grp_title,
                                                title__exact=parameter_name)
                                        except:
                                            parameter_model_object = False

                                        if parameter_model_object:
                                            for item in product_features:
                                                if item.value == parameter_value and item.feature_name_id == parameter_model_object.id:
                                                    saved_features.append(parameter_value)
                                                    saved_features_ids.append(item.id)
                                if not saved_features_ids: # если нет совпадений с параметрами которые уже есть у товара - то удаляем эти параметры
                                    for feature in product_features:
                                        feature.delete()
                                else: # проверяем какие свойства остались - убираем те, которые не вошли в импорт
                                    delete_prod_features = product_features.exclude(id__in=saved_features_ids)
                                    for feature in delete_prod_features:
                                        feature.delete()

                                for parameter in parameter_array:
                                    parameter_name = parameter.getAttribute('name')
                                    parameter_name_grp_title = parameter.getAttribute('paramgrp')
                                    parameter_value = parameter.getAttribute('value')
                                    if parameter_name != '' and parameter_value != '' and parameter_name_grp_title != '': # создаём значения параметров
                                        try:
                                            parameter_model_object = category_feature_names.get(
                                                feature_group__title__exact=parameter_name_grp_title,
                                                title=parameter_name)
                                        except:
                                            parameter_model_object = False

                                        if parameter_value not in saved_features: # если параметра нет в сохраненых параметрах - создаём новые
                                            if parameter_model_object:
                                                new_parameter_value = FeatureValue(product=exits_prod,
                                                    feature_name=parameter_model_object, value=parameter_value)
                                                new_parameter_value.save()
                                            else:
                                                # создадим группу параметров и название параметра
                                                if prod_category:
                                                    new_param_group = FeatureGroup(category=prod_category,
                                                        title=parameter_name_grp_title)
                                                    new_param_group.save()
                                                    parameter_model_object = FeatureNameCategory(
                                                        feature_group=new_param_group, title=parameter_name)
                                                    parameter_model_object.save()
                                                    new_parameter_value = FeatureValue(product=exits_prod,
                                                        feature_name=parameter_model_object, value=parameter_value)
                                                    new_parameter_value.save()
                        exits_prod.save()
                        updated += 1

                    if new_product: # если продукт создан - то проверяем и создаём свойства, значения параметров, картинки
                        # значения параметров
                        parameter_array = z.getElementsByTagName('parameter')
                        if parameter_array and prod_category: # если в xml есть теги parameter и определена категория товара
                            for parameter in parameter_array:
                                parameter_name = parameter.getAttribute(
                                    'name')
                                parameter_name_grp_title = parameter.getAttribute(
                                    'paramgrp')
                                parameter_value = parameter.getAttribute('value')
                                if parameter_name != '' and parameter_value != '' and parameter_name_grp_title != '': # создаём значения параметров
                                    try:
                                        parameter_model_object = category_feature_names.get(
                                            feature_group__title__exact=parameter_name_grp_title,
                                            title=parameter_name)
                                    except:
                                        #parameter_model_object = False
                                        # создадим группу параметров и название параметра
                                        if prod_category:
                                            new_param_group = FeatureGroup(category=prod_category,
                                                title=parameter_name_grp_title)
                                            new_param_group.save()
                                            parameter_model_object = FeatureNameCategory(
                                                feature_group=new_param_group, title=parameter_name)
                                            parameter_model_object.save()
                                        else:
                                            parameter_model_object = False
                                    if parameter_model_object:
                                        new_parameter_value = FeatureValue(product=new_product,
                                            feature_name=parameter_model_object, value=parameter_value)
                                        new_parameter_value.save()
                                        # значения свойств
                        property_array = z.getElementsByTagName(
                            'property')
                        if property_array:
                            for property in property_array:
                                property_value = property.firstChild.nodeValue
                                new_property = ProductProperty(product=new_product, value=property_value)
                                new_property.save()
                                # изображения товара
                        img_array = z.getElementsByTagName('img')
                        if img_array:
                            for img in img_array:
                                img_link = img.firstChild.nodeValue
                                img_is_default = img.getAttribute('default')
                                if img_is_default == 'yes' and img_link != '': # сохраняем как главное изображение товара
                                    # Save image
                                    img_temp = NamedTemporaryFile(delete=True)
                                    try:
                                        img_temp.write(urlopen(img_link).read())
                                        img_temp.flush()
                                        new_product.image.save(u"product_image_%s" % new_product.id,
                                            File(img_temp))
                                        new_product.save()
                                    except:
                                        pass
                                elif img_link != '':
                                    img_temp = NamedTemporaryFile(delete=True)
                                    new_image = ProductImage(product=new_product)
                                    try:
                                        img_temp.write(urlopen(img_link).read())
                                        img_temp.flush()
                                        new_image = ProductImage(product=new_product)
                                        new_image.image.save(
                                            u"product_image_%s-additional" % new_product.id,
                                            File(img_temp))
                                        new_image.save()
                                    except:
                                        pass
        return u'%s: added: %s; updated:%s;' % (last_change_date, added, updated)
    else:
        return u'empty'

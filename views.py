# -*- coding: utf-8 -*-
from decimal import Decimal
import os
from urllib2 import urlopen
from django import http
from django.conf import settings
from django.views.generic.simple import direct_to_template
from pytils.translit import translify, slugify
from django.views.decorators.csrf import csrf_exempt
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from xml.dom.minidom import *
from apps.products.models import Action, Category, Product, FeatureGroup, FeatureNameCategory, ProductImage, ProductProperty, FeatureValue
from django.http import HttpResponseRedirect, HttpResponse

try:
    from PIL import Image
except ImportError:
    import Image
import md5
import datetime


def handle_uploaded_file(f, filename, folder):
    name, ext = os.path.splitext(translify(filename).replace(' ', '_'))
    hashed_name = md5.md5(name + datetime.datetime.now().strftime("%Y%m%d%H%M%S")).hexdigest()
    path_name = settings.MEDIA_ROOT + '/uploads/' + folder + hashed_name + ext
    destination = open(path_name, 'wb+')

    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    return '/media/uploads/' + folder + hashed_name + ext


@csrf_exempt
def upload_img(request):
    if request.user.is_staff:
        if request.method == 'POST':
            url = handle_uploaded_file(request.FILES['file'], request.FILES['file'].name, 'images/')

            #Resizing
            size = 650, 650
            im = Image.open(settings.ROOT_PATH + url)
            imageSize = im.size
            if (imageSize[0] > size[0]) or  (imageSize[1] > size[1]):
                im.thumbnail(size, Image.ANTIALIAS)
                im.save(settings.ROOT_PATH + url, "JPEG", quality=100)
            return http.HttpResponse('<img src="%s"/>' % url)

        else:
            return http.HttpResponse('error')
    else:
        return http.HttpResponse('403 Forbidden. Authentication Required!')


@csrf_exempt
def upload_file(request):
    if request.user.is_staff:
        if request.method == 'POST':
            url = handle_uploaded_file(request.FILES['file'], request.FILES['file'].name, 'files/')
            url = '<a href="%s" target=_blank>%s</a>' % (url, request.FILES['file'].name)
            return http.HttpResponse(url)
    else:
        return http.HttpResponse('403 Forbidden. Authentication Required!')

'''
@csrf_exempt
def crop_image_view(request, id_image):
    next = request.REQUEST.get('next', None)
    if request.method != "POST":
        try:
            image = Members.objects.get(id=id_image).image
            return direct_to_template(request, 'crop_image.html', locals())
        except Members.DoesNotExist:
            return http.HttpResponseRedirect(next)
    else:
        x1 = int(request.POST['x1'])
        y1 = int(request.POST['y1'])
        x2 = int(request.POST['x2'])
        y2 = int(request.POST['y2'])
        box = (x1, y1, x2, y2)
        original_img = Members.objects.get(id=id_image)
        infile = settings.ROOT_PATH + original_img.image.url
        file, ext = os.path.splitext(infile)
        im = Image.open(infile)
        ms = im.crop(box)
        name = file + "_crop.jpg"
        ms.save(name, "JPEG")
        output_size = [76, 77]

        image = Image.open(name)
        m_width = float(output_size[0])
        m_height = float(output_size[1])
        w_k = image.size[0]/m_width
        h_k = image.size[1]/m_height
        if output_size < image.size:
            if w_k > h_k:
                new_size = (int(m_width), int(image.size[1]/w_k))
            else:
                new_size = (int(image.size[0]/h_k), int(m_height))
        else:
            new_size = image.size
        image = image.resize(new_size, Image.ANTIALIAS)
        image.save(name, "JPEG", quality=100)
        return http.HttpResponseRedirect(next)
'''


def upload_xml(request):
    if request.user.is_staff:
        if request.method == 'POST':
            f = request.FILES['file']
            filename = request.FILES['file'].name
            name, ext = os.path.splitext(translify(filename).replace(' ', '_'))
            newname = '/uploads/' + 'xml_tmp' + ext
            if ext == '.xsql' or ext == '.xml':
                # удаляем старый файл
                oldfile = 'xml_tmp'
                for root, dirs, files in os.walk(settings.MEDIA_ROOT + '/uploads/', ):
                    for filename in files:
                        name, ext = os.path.splitext(translify(u'%s' % filename).replace(' ', '_'))
                        if name == 'xml_tmp':
                            oldfile = '/uploads/' + filename
                try:
                    os.remove(settings.MEDIA_ROOT + oldfile)
                except OSError:
                    oldfile = False
                    # загружаем новый
                path_name = settings.MEDIA_ROOT + newname
                destination = open(path_name, 'wb+')
                for chunk in f.chunks():
                    destination.write(chunk)
                destination.close()

                # распарсиваем:
                f = parse(path_name)

                # todo: и еще надо будет учитывать, что при повторном импорте нужно сначала смотреть. есть ли уже такая категория или нет - чтобы дублей не наделать
                rows_array = f.getElementsByTagName('ROW')
                actions_array = f.getElementsByTagName('action')
                all_categories = Category.objects.all()
                all_products = Product.objects.all()
                all_actions = Action.objects.all()
                parsed = ''
                if rows_array: # если есть элемент ROW - то проверяем что пришло - товар или категория
                    for z in rows_array:
                        if z.getAttribute('up_id') or not z.getAttribute('grp_id'): # парсим категорию
                            parsed = 'category'
                            cat_title = z.getAttribute('name')
                            cat_slug = slugify(cat_title)
                            cat_xml_id = z.getAttribute('id')
                            cat_xml_num = z.getAttribute('num')
                            cat_up_id = z.getAttribute('up_id')

                            try:
                                exits_cat = all_categories.get(xml_id=cat_xml_id)
                            except:
                                exits_cat = False

                            try:
                                parent_cat = Category.objects.get(xml_id=int(cat_up_id))
                            except:
                                parent_cat = False

                            new_category = False
                            if not exits_cat: # если категории с таким же xml_id не существует
                                if parent_cat:
                                    new_category = Category(parent=parent_cat, title=cat_title, slug=cat_slug,
                                        is_published=False,
                                        xml_id=cat_xml_id, xml_num=cat_xml_num, xml_up_id=cat_up_id)
                                else:
                                    new_category = Category(title=cat_title, slug=cat_slug,
                                        is_published=False,
                                        xml_id=cat_xml_id, xml_num=cat_xml_num, xml_up_id=cat_up_id)
                                new_category.save()

                            if new_category: # если категория создана - то проверяем и создаём группы параметров и параметры
                                paramgrp_array = z.getElementsByTagName('paramgrp')
                                if paramgrp_array:
                                    for paramgrp in paramgrp_array:
                                        paramgrp_name = paramgrp.getAttribute('name')
                                        new_paramgrp = False
                                        if paramgrp_name != '': # создаём группу параметров
                                            new_paramgrp = FeatureGroup(title=paramgrp_name, category=new_category)
                                            new_paramgrp.save()
                                        if new_paramgrp:
                                            parameter_array = paramgrp.getElementsByTagName(
                                                'parameter')
                                            if parameter_array:
                                                for parameter in parameter_array:
                                                    parameter_name = parameter.getAttribute(
                                                        'name')
                                                    if parameter_name != '': # создаём параметры
                                                        new_parameter = FeatureNameCategory(title=parameter_name,
                                                            feature_group=new_paramgrp)
                                                        new_parameter.save()

                        elif z.getAttribute('price'): # парсим товар
                            parsed = 'product'
                            product_xml_num = z.getAttribute('num')
                            product_title = z.getAttribute('name')
                            #product_xml_code = z.getAttribute('code')
                            product_price = Decimal(z.getAttribute('price'))
                            try:
                                product_description = z.getElementsByTagName('description')[0].firstChild.nodeValue
                            except:
                                product_description = u''
                            grp_id = z.getAttribute('grp_id')
                            #superprice = z.getAttribute('superprice')
                            #discountmax = z.getAttribute('discountmax')
                            #action = z.getAttribute('action')

                            try:
                                exits_prod = all_products.get(xml_num=product_xml_num)
                            except:
                                exits_prod = False

                            new_product = False
                            if not exits_prod: # если продукта с таким же xml_num не существует, то создаём продукт
                                try:
                                    prod_category = all_categories.get(xml_id=grp_id)
                                except:
                                    prod_category = False
                                if prod_category:
                                    category_feature_names = prod_category.get_feature_names()
                                    new_product = Product(category=prod_category, title=product_title,
                                        description=product_description,
                                        price=product_price, status='in_stock', xml_num=product_xml_num)
                                else:
                                    category_feature_names = False
                                    new_product = Product(title=product_title, description=product_description,
                                        price=product_price, status='in_stock', xml_num=product_xml_num)
                                new_product.save()
                            else:
                                prod_category = False
                                category_feature_names = False

                            if new_product: # если продукт создан - то проверяем и создаём свойства, значения параметров, картинки
                                # значения параметров
                                parameter_array = z.getElementsByTagName(
                                    'parameter')
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
                                                new_product.image.save(u"product_image_%s" % new_product.pk,
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
                                                    u"product_image_%s-%s" % (new_product.pk, new_image.pk),
                                                    File(img_temp))
                                                new_image.save()
                                            except:
                                                pass

                    if parsed == 'category':
                        return http.HttpResponseRedirect('/admin/products/category/')
                    elif parsed == 'product':
                        return http.HttpResponseRedirect('/admin/products/product/')
                    else:
                        return http.HttpResponseRedirect('/admin/')
                elif actions_array: # если есть элемент action - добавляем акцию
                    for z in actions_array:
                        action_name = z.getAttribute('name')
                        try:
                            action_title = z.getElementsByTagName('title')[0].firstChild.nodeValue
                        except:
                            action_title = False
                        try:
                            action_description = z.getElementsByTagName('description')[0].firstChild.nodeValue
                            action_short_description = action_description.split(' ')[:30]
                            action_short_description = ' '.join(action_short_description)
                        except:
                            action_description = False
                        try:
                            action_img_url = z.getElementsByTagName('img')[0].firstChild.nodeValue
                        except:
                            action_img_url = ''
                        try:
                            exits_action = all_actions.get(title=action_title)
                        except:
                            exits_action = False
                        if action_title and action_description and not exits_action: # добавляем акцию
                            new_action = Action(title=action_title, short_description=action_short_description,
                                description=action_description)
                            new_action.save()
                            if action_img_url != '': # если в xml была ссылка на картику - то сохраняем её
                                # Save image
                                img_temp = NamedTemporaryFile(delete=True)
                                try:
                                    img_temp.write(urlopen(action_img_url).read())
                                    img_temp.flush()
                                    new_action.image.save(u"action_image_%s" % new_action.pk, File(img_temp))
                                    new_action.save()
                                except:
                                    pass

                    return http.HttpResponseRedirect('/admin/products/action/')
                else:
                    return http.HttpResponseRedirect('/admin/')
            else:
                return http.HttpResponseRedirect('/admin/')
    else:
        return http.HttpResponse('403 Forbidden. Authentication Required!')

# -*- coding: utf-8 -*-
from django.http import  HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Max, Min

from django.views.generic import ListView, DetailView, TemplateView, View

from models import Category, Product, Action, FeatureNameCategory, FeatureValue, Manufacturer
from apps.orders.forms import OneClickByeForm

class ShowCategory(TemplateView):
    template_name = 'products/show_category.html'

    def get_context_data(self, **kwargs):
        context = super(ShowCategory, self).get_context_data()
        is_additional_filter = False
        try:
            sort = self.request.GET['sort']
        except:
            sort = False
        try:
            mfr = int(self.request.GET['mfr'])
        except:
            mfr = False
        try:
            price_filter = int(self.request.GET['price_filter'])
        except:
            price_filter = False
        try:
            ship_filter = int(self.request.GET['ship_filter'])
            ship_filter_exist = True
        except:
            ship_filter = False
            ship_filter_exist = False
        try:
            features = self.request.GET['features']
        except:
            features = False

        # сортировка для списка
        try:
            view = self.request.GET['view']
        except:
            view = False
        try:
            title_sort = self.request.GET['title_sort']
        except:
            title_sort = False
        try:
            ship_sort = self.request.GET['ship_sort']
        except:
            ship_sort = False
        try:
            price_sort = self.request.GET['price_sort']
        except:
            price_sort = False

        slug = self.kwargs.get('slug', None)
        sub_slug = self.kwargs.get('sub_slug', None)
        is_subcat = False
        if sub_slug == 'all':
            try:
                category = Category.objects.get(slug=slug)
            except:
                category = False
        else:
            try:
                category = Category.objects.filter(parent__slug=slug).get(slug=sub_slug)
                is_subcat = True
            except:
                is_subcat = False
                try:
                    category = Category.objects.filter(parent__slug=slug).get(slug=slug)
                except:
                    category = False
        if category:
            context['is_subcat'] = is_subcat
            context['category'] = category
            products = category.get_products()

            if sort:
                if sort == 'pasc':
                    products = products.order_by('-price')
                if sort == 'pdesk':
                    products = products.order_by('price')

            manufacturers = Manufacturer.objects.published().filter(id__in=products.values('manufacturer__id')).values(
                'id', 'title')
            setattr(context['category'], 'manufacturers', manufacturers)
            if manufacturers:
                is_additional_filter = True
            dic = products.aggregate(Min('price'), Max('price'))
            context['max_price'] = dic['price__max']
            context['min_price'] = dic['price__min']
            if context['max_price'] == None:
                context['max_price'] = 0
                context['min_price'] = 0
            dic2 = products.aggregate(Min('status'), Max('status'))
            context['max_status'] = dic2['status__max']
            context['min_status'] = dic2['status__min']
            if context['max_status'] == None:
                context['max_status'] = 0
                context['min_status'] = 0

            filter_parameters_groops = category.get_all_feature_groups()
            filter_parameters_names = FeatureNameCategory.objects.published().filter(in_filter=True,
                feature_group__id__in=filter_parameters_groops.values('id'))
            selected_fn_ids = []
            for name in filter_parameters_names:
                values = FeatureValue.objects.filter(product__id__in=products.values('id'),
                    feature_name__id=name.id).values('value').distinct().order_by('value')
                if features:
                    for features_item in features.split('|'):
                        feature = features_item.split('^')
                        try:
                            if int(feature[0]) == name.id:
                                setattr(name, 'selected', feature[1])
                                selected_fn_ids.append(int(feature[0]))
                        except:
                            pass
                setattr(name, 'values', values)
                if values:
                    is_additional_filter = True

            context['filter_parameters'] = filter_parameters_names
            context['selected_filter_parameters'] = filter_parameters_names.filter(id__in=selected_fn_ids)

            if mfr:
                products = products.filter(manufacturer__id=mfr)
                context['mfr'] = mfr

            if price_filter:
                products = products.filter(price__lte=price_filter)
                context['price_filter'] = price_filter

            if ship_filter_exist:
                products = products.filter(status__lte=ship_filter)
                context['ship_filter'] = ship_filter

            if features:
                all_feature_values = FeatureValue.objects.all().values('product__id').distinct()
                result_feature_values = all_feature_values
                for features_item in features.split('|'):
                    feature = features_item.split('^')
                    feature_values = all_feature_values.filter(feature_name__id=int(feature[0]),
                        value__contains=feature[1]).values('product__id')
                    result_feature_values = result_feature_values.filter(product__id__in=feature_values)
                products = products.filter(id__in=result_feature_values)

            context['additional_filter'] = is_additional_filter

            # применяю сортировку
            if view and view == 'list':
                if title_sort:
                    if title_sort == 'desc':
                        products = products.order_by('title')
                    elif title_sort == 'asc':
                        products = products.order_by('-title')
                if ship_sort:
                    if ship_sort == 'desc':
                        products = products.order_by('-status')
                    elif ship_sort == 'asc':
                        products = products.order_by('status')
                if price_sort:
                    if price_sort == 'desc':
                        products = products.order_by('-price')
                    elif price_sort == 'asc':
                        products = products.order_by('price')

            context['catalog'] = products
        else:
            context['category'] = False
        return context

show_category = ShowCategory.as_view()

class ShowProduct(TemplateView):
#    model = Product
#    context_object_name = 'product'
    template_name = 'products/show_product.html'

    def get_context_data(self, **kwargs):
        context = super(ShowProduct, self).get_context_data()

        try:
            pk = self.kwargs.get('pk', None)
            self.object = Product.objects.get(xml_code=pk)
            context['product'] = self.object
        except:
            return HttpResponseRedirect('/')

        # все указанные параметры товара
        product_features_values_set = self.object.get_feature_values()

        # группа с основными параметрами
        base_features_values = []
        base_feature_group = self.object.category.get_base_feature_group()
        try:
            for name in base_feature_group.get_feature_names():
                try:
                    value = product_features_values_set.get(feature_name=name)
                    base_features_values.append({'title': name.title, 'value': value})
                except:
                    value = False
            setattr(base_feature_group, 'features_values', base_features_values)
        except:
            pass
        if base_features_values:
            context['base_feature_group'] = base_feature_group
        else:
            context['base_feature_group'] = False

        #base_feature_group = self.object.category.get_base_feature_group()

        # группа с НЕосновными параметрами
        exists = False
        try:
            other_feature_groups = self.object.category.get_other_feature_groups()
            for group in other_feature_groups:
                other_features_values = []
                for name in group.get_feature_names():
                    try:
                        value = product_features_values_set.get(feature_name=name)
                        exists = True
                        other_features_values.append({'title': name.title, 'value': value})
                    except:
                        value = False
                setattr(group, 'features_values', other_features_values)
        except:
            other_feature_groups = []

        if exists:
            context['other_feature_groups'] = other_feature_groups
        else:
            context['other_feature_groups'] = []

        context['attached_photos'] = self.object.get_photos()

        # форма покупки "в один клик"
        product_qs = Product.objects.filter(id=self.object.id)
        try:
            mfrer = '%s - ' % self.object.manufacturer.title
        except:
            mfrer = ''
        one_clk_form = OneClickByeForm(initial={'product': self.object,
                                                'product_description': u'%s%s %s' % (
                                                    mfrer, self.object.category.title_singular, self.object.title),
                                                'product_price': self.object.price})
        one_clk_form.fields['product'].queryset = product_qs
        context['one_clk_form'] = one_clk_form
        return context

show_product = ShowProduct.as_view()

class ProductsSearch(TemplateView):
    template_name = 'products/search_results.html'

    def get_context_data(self, **kwargs):
        context = super(ProductsSearch, self).get_context_data()
        products = Product.objects.published()
        try:
            q = self.request.GET['q']
        except:
            q = ''
        if q == '':
            q = '?'
        qs = products.filter(
            Q(title__icontains=q) |
            Q(category__title__icontains=q) |
            Q(category__title_singular__icontains=q) |
            #            Q(description__icontains=q) |
            #            Q(material__icontains=q) |
            #            Q(art__icontains=q) |
            Q(price__icontains=q)
        )
        qs = qs.exclude(category=None) #исключим все товары у которых нет категории
        context['catalog'] = qs
        context['query'] = q
        return context

search_products = ProductsSearch.as_view()

class ActionsListView(ListView):
    model = Action
    context_object_name = 'actions'
    template_name = 'products/actions_list.html'
    queryset = Action.objects.published()

    def get_context_data(self, **kwargs):
        queryset = kwargs.pop('object_list')

        arch_count = queryset.filter(in_archive=True).count
        if self.kwargs.get('archive', None):
            queryset = queryset.filter(in_archive=True)
        else:
            queryset = queryset.filter(in_archive=False)

        page_size = self.get_paginate_by(queryset)
        context_object_name = self.get_context_object_name(queryset)
        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
            context = {
                'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated,
                'object_list': queryset
            }
        else:
            context = {
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                'object_list': queryset
            }
        if self.kwargs.get('archive', None):
            context['is_archive'] = True
        else:
            context['archive_count'] = arch_count

        context.update(kwargs)
        if context_object_name is not None:
            context[context_object_name] = queryset
        return context

actions_list = ActionsListView.as_view()
actions_list_archive = ActionsListView.as_view()

class ShowAction(DetailView):
    model = Action
    context_object_name = 'action'
    template_name = 'products/show_action.html'

show_action = ShowAction.as_view()


class LoadCatalogView(View):
    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseRedirect('/')
        else:
            if 'size' not in request.POST or 's_type' not in request.POST or 'id_cat' not in request.POST:
                return HttpResponseBadRequest()
            try:
                id_cat = int(request.POST['id_cat'])
            except:
                return HttpResponseBadRequest()

            try:
                curr_categ = Category.objects.get(id=id_cat)
            except Category.DoesNotExist:
                return HttpResponseBadRequest()

            products = curr_categ.get_products()
            size = request.POST['size']
            s_type = request.POST['s_type']
            if size != 'all':
                try:
                    size = int(size)
                except ValueError:
                    return HttpResponseBadRequest()
                if s_type == 'all':
                    queryset = products.filter(size__in=[size])
                else:
                    queryset = products.filter(s_type=s_type, size__in=[size])
            else:
                if s_type == 'all':
                    queryset = products
                else:
                    queryset = products.filter(s_type=s_type)

            items_html = render_to_string(
                'products/products_list.html',
                    {'catalog': queryset, 'request': request, }
            )
            return HttpResponse(items_html)

load_catalog = csrf_exempt(LoadCatalogView.as_view())

class LoadFNamesAdmin(View):
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            if 'id_category' not in request.POST:
                return HttpResponseBadRequest()

            id_category = request.POST['id_category']

            try:
                id_category = int(id_category)
            except ValueError:
                return HttpResponseBadRequest()

            try:
                curr_category = Category.objects.get(id=id_category)
            except Category.DoesNotExist:
                return HttpResponseBadRequest()

            groups = curr_category.get_all_feature_groups()
            html_code = u'<option value="" selected="selected">---------</option>'
            for group in groups:
                names = group.get_feature_names()
                for name in names:
                    html_code = u'%s<option value="%s">%s - %s</option>' % (html_code, name.id, group.title, name.title)
            return HttpResponse(html_code)
        else:
            return HttpResponseBadRequest()

load_features_names = LoadFNamesAdmin.as_view()

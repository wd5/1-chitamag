# -*- coding: utf-8 -*-
from django.views.generic import TemplateView
from apps.products.models import Product
from apps.siteblocks.models import Banner

class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['is_index'] = True
        context['hit_products'] = Product.objects.published().filter(is_hit=True)
        all_banners = Banner.objects.published()
        all_products = Product.objects.published()
        slider_products = all_products.filter(in_slider=True)
        discount_products = all_products.filter(is_discount=True)
        discount_products = discount_products.order_by('?')
        big_banners = all_banners.filter(size='big').order_by('?')[:2]
        small_banners = all_banners.filter(size='small').order_by('?')[:1]
#        if small_banners.count() == 1:
#            context['small_banner'] = small_banners[0]
#            try:
#                context['small_discount'] = discount_products[:1][0]
#            except:
#                context['small_discount'] = False
#        elif small_banners.count() == 0:
#            context['small_discounts'] = discount_products[:2]

        context['big_banners'] = big_banners
        context['slider_products'] = slider_products

        # проверка работы отправки xml
#        import urllib2
#        xml_string = u"<Order Id='12' FirstName='Admin' LastName='CHITAMAG' Email='admin@admin.ru' Phone='+7 (981) 131-64-98' CartingType='carting' OrderStatus='processed' Address='Северный 37' Note='примечание' TotalPrice='14 250' CreateDate='28 декабря 2012 г. 22:16:03'><Item ProductCode = '1439600' Count='1' Description=' - LG Optimus L7 p700' ProductPrice='8990,00' /><Item ProductCode = '1241400' Count='1' Description=' - LG P350' ProductPrice='5260,00' /></Order>"
#        url = "http://ontpay.info/te/cm/INDOC.XSQL"
#        xml_string = xml_string.encode('utf-8')
#        req = urllib2.Request(url=url, data=xml_string, headers={'Content-Type': 'text/xml'})
#        response = urllib2.urlopen(req)
#        content = response.read()

        return context

index = IndexView.as_view()
# -*- coding: utf-8 -*-
from apps.siteblocks.models import Settings
from settings import SITE_NAME

def settings(request):
    if not request.session.exists(request.session.session_key):
        request.session.create()
    try:
        phone = Settings.objects.get(name='contacts_phone').value
    except Settings.DoesNotExist:
        phone = False

    return {
        'site_name': SITE_NAME,
        'contacts_phone': phone,
    }
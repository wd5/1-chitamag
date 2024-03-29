# -*- coding: utf-8 -*-
DATABASE_NAME = u'chitamag'
PROJECT_NAME = u'chitaMag'
SITE_NAME = u'ЧитаМаг'
DEFAULT_FROM_EMAIL = u'support@chitamag.ru'

from config.base import *

try:
    from config.development import *
except ImportError:
    from config.production import *

TEMPLATE_DEBUG = DEBUG

INSTALLED_APPS += (
    'apps.siteblocks',
    'apps.pages',
    #'apps.faq',
    'apps.products',
    'apps.users',
    'apps.orders',

    'sorl.thumbnail',
    #'south',
    #'captcha',
)

#AUTHENTICATION_BACKENDS = (
#    'apps.auth_backends.CustomUserModelBackend',
#)

MIDDLEWARE_CLASSES += (
    'apps.pages.middleware.PageFallbackMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS += (
    'apps.pages.context_processors.meta',
    'apps.siteblocks.context_processors.settings',
    'apps.utils.context_processors.authorization_form',
)

#from settings_DebugToolbar import *
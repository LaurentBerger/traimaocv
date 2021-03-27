"""
ASGI config for traimaocv project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os, sys

from django.core.asgi import get_asgi_application
from channels.routing import get_default_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traimaocv.settings')

# https://stackoverflow.com/questions/14927345/importerror-no-module-named-django-core-wsgi-apache-virtualenv-aws-wsgi
# add the hellodjango project path into the sys.path
if "USERDOMAIN" in os.environ:
    if os.environ[ "USERDOMAIN"]=='PC-LAURENT-VISI':
        # add the virtualenv site-packages path to the sys.path
        sys.path.append('"F:\\Program Files\\Python\\lib\\site-packages"')
    else:
        sys.path.append('/home/traimaocv/django')
        # add the virtualenv site-packages path to the sys.path
        sys.path.append('/home/traimaocv/env_django/lib/python3.8/site-packages')
else:
    sys.path.append('/home/traimaocv/django')
    # add the virtualenv site-packages path to the sys.path
    sys.path.append('/home/traimaocv/env_django/lib/python3.8/site-packages')


django.setup()

application = get_default_application()
application = get_asgi_application()

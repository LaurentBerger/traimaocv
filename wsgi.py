"""
WSGI config for traimaocv project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os, sys

# https://stackoverflow.com/questions/14927345/importerror-no-module-named-django-core-wsgi-apache-virtualenv-aws-wsgi
# add the hellodjango project path into the sys.path
sys.path.append('/home/traimaocv/django')

# add the virtualenv site-packages path to the sys.path
sys.path.append('/home/traimaocv/env_django/lib/python3.8/site-packages')


from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traimaocv.settings')

application = get_wsgi_application()

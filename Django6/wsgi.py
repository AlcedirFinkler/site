"""
WSGI config for Django6 project.
"""

import os
import sys

# Adicionar este código para debug
print("Python Path:", sys.path)
print("Current directory:", os.getcwd())
print("DJANGO_SETTINGS_MODULE:", os.environ.get('DJANGO_SETTINGS_MODULE'))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Django6.settings')
print("DJANGO_SETTINGS_MODULE after setdefault:", os.environ.get('DJANGO_SETTINGS_MODULE'))

try:
    application = get_wsgi_application()
    print("WSGI application initialized successfully")
except Exception as e:
    print(f"Error initializing WSGI application: {e}")
    raise
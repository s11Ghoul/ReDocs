# redocs/__init__.py
from __future__ import absolute_import, unicode_literals

# Это позволит убедиться, что app всегда импортируется при запуске Django
from .celery import app as celery_app

__all__ = ['celery_app']
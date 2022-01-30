import os

from celery import Celery

os.getenv("DJANGO_SETTINGS_MODLUE")
app = Celery("dsp")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

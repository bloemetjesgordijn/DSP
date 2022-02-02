import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dsp.settings")
app = Celery("dsp")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

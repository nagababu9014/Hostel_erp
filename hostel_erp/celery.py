import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hostel_erp.settings')

app = Celery('hostel_erp')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

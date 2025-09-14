import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "student_auth.settings")

app = Celery("student_auth")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

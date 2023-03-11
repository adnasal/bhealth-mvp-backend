from __future__ import absolute_import

import os
from pathlib import Path

from celery import Celery, shared_task
from django.conf import settings
from django.core.files import File
from django.core.files.storage import FileSystemStorage

from src.users.models import Result

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.config.local")

app = Celery('src.config')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# tasks can be added below
@shared_task(name="Upload Result")
def upload(appointment, patient, path, file_name):
    print('Uploading file...')

    storage = FileSystemStorage()

    path_object = Path(path)

    with path_object.open(mode='rb') as file:
        picture = File(file, name=path_object.name)

        instance = Result(appointment=appointment, patient=patient, pdf=picture)

        instance.save()

    storage.delete(file_name)

    print('Uploaded!')

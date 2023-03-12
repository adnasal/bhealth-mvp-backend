import datetime
from datetime import date, timedelta, datetime

import requests
from bs4 import BeautifulSoup
from celery import shared_task

from django.conf import settings

today = date.today()

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from celery import shared_task
from .models import Result
from .serializers import ResultSerializer

from django.core.files.base import ContentFile
from celery import shared_task
from .models import Result, Appointment


@shared_task
def upload_pdf(result_id, data):
    serializer = ResultSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    result = Result.objects.last()
    result.appointment = Appointment.objects.get(pk=result_id)
    result.save(update_fields=['appointment'])

    return "Done"

from datetime import date
from io import BytesIO

from PIL import Image
from django.core.files.base import ContentFile
from django.http import HttpResponse

from bhealthapp.rmq_send_message import send_messages

today = date.today()

from celery import shared_task
from bhealthapp.models import User


@shared_task
def upload_pdf(appointment_id):
    send_messages('results', {'appointment_id': appointment_id})
    return "Done"


@shared_task
def send_request_notification(appointment_id):
    send_messages('requests', {'appointment_id': appointment_id})

    return "Done"


@shared_task
def request_updated(appointment_id):
    send_messages('appointment_updates', {'appointment_id': appointment_id})

    return "Done"


@shared_task
def send_appointment_message(appointment_id):
    send_messages('appointment', {'appointment_id': appointment_id})

    return "Done"


@shared_task
def send_appointment_canceled_message(appointment_id):
    send_messages('appointment_canceled', {'appointment_id': appointment_id})

    return "Done"


@shared_task
def resize_profile_picture(user_id):
    try:
        user = User.objects.get(id=user_id)
        if user.profile_picture:
            image = Image.open(user.profile_picture)
            image.thumbnail((300, 300))
            resized_image = BytesIO()
            image.save(resized_image, format='JPEG')

            user.profile_picture.save(user.profile_picture.name, ContentFile(resized_image.getvalue()), save=False)
            user.save()

    except User.DoesNotExist:
        print(f"User with id {user_id} does not exist.")


@shared_task
def download_file(file_path, pdf_name):
    with open(file_path, 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename={}'.format(pdf_name)
        return response

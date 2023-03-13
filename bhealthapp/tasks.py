import json
from datetime import date
from django.core.serializers import serialize
from django.conf import settings
import pika
from django.conf import settings

today = date.today()

from .serializers import ResultSerializer

from celery import shared_task
from .models import Result, Appointment, Notification


@shared_task
def upload_pdf(result_id, data):
    serializer = ResultSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    result = Result.objects.last()
    result.appointment = Appointment.objects.get(pk=result_id)
    result.save(update_fields=['appointment'])

    # Publish notification to RabbitMQ
    message = {
        'type': 'result_created',
        'data': serialize('json', [result.appointment])
    }

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.CELERY_BROKER_URL))
    channel = connection.channel()

    channel.queue_declare(queue='notifications')
    channel.basic_publish(exchange='', routing_key='notifications', body=json.dumps(message))

    connection.close()

    return "Done"


@shared_task
def send_request_notification(appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    if appointment.status == 0:
        message = {
            'id': appointment.id,
            'lab_id': appointment.lab_appointment.id,
            'patient_id': appointment.patient.id,
            'service_name': appointment.service_appointment.name,
            'date': str(appointment.date),
        }
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            credentials=pika.PlainCredentials(
                settings.RABBITMQ_USER,
                settings.RABBITMQ_PASSWORD,
            ),
        ))
        channel = connection.channel()
        channel.exchange_declare(exchange=settings.RABBITMQ_EXCHANGE, exchange_type='direct')
        channel.basic_publish(
            exchange='requests',
            routing_key='new_request',
            body=json.dumps(message),
        )
        connection.close()

    return "Done"


@shared_task
def request_updated(appointment_id):
    appointment = Appointment.objects.get(pk=appointment_id)

    # Send message to RabbitMQ
    message = f'Appointment request updated: {appointment}'
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='appointment_updates')
    channel.basic_publish(exchange='',
                          routing_key='appointment_updates',
                          body=message)
    connection.close()

    return "Done"

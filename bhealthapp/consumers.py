import json

import pika
from django.conf import settings

from bhealthapp.models import Result, Appointment, Notification


class NotificationConsumer:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.CELERY_BROKER_URL))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue='notifications')
        self.channel.basic_consume(queue='notifications', on_message_callback=self.process_notification)

    def process_notification(self, channel, method, properties, body):
        notification_data = json.loads(body)
        notification_type = notification_data['type']
        notification_payload = notification_data['data']

        if notification_type == 'result_created':
            appointments = list(Appointment.objects.filter(pk=notification_payload[0]['pk']))
            notification_message = f'Result added for appointment(s) {", ".join([str(appointment) for appointment in appointments])}'

            # Create new notification
            notification = Notification.objects.create(
                recipient=appointments[0].patient,
                message=notification_message
            )

        channel.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        self.channel.start_consuming()


consumer = NotificationConsumer()

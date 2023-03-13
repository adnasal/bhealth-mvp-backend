import json

import pika
from django.conf import settings

from bhealthapp.models import Result, Appointment, Notification, Lab, User


class NewResultConsumer:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.CELERY_BROKER_URL))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue='results')
        self.channel.basic_consume(queue='results', on_message_callback=self.process_notification)

    def process_notification(self, channel, method, properties, body):
        notification_data = json.loads(body)
        notification_type = notification_data['type']
        notification_payload = notification_data['data']

        if notification_type == 'result_created':
            appointments = list(Appointment.objects.filter(pk=notification_payload[0]['pk']))
            notification_message = f'Result added for appointment(s) {", ".join([str(appointment) for appointment in appointments])}'

            # Create new notification
            notification = Notification.objects.create(
                notification_lab=appointments[0].lab,
                notification_user=appointments[0].patient,
                notification_appointment=appointments[0],
                message=notification_message,
                is_confirmed=False,
                is_declined=False
            )

        channel.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        self.channel.start_consuming()


consumer = NewResultConsumer()


class RequestConsumer:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.CELERY_BROKER_URL))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue='requests')
        self.channel.basic_consume(queue='requests', on_message_callback=self.process_request)

    def process_request(self, channel, method, properties, body):
        request_data = json.loads(body)
        lab_id = request_data['lab_id']
        service_name = request_data['service_name']
        date = request_data['date']

        # Send notification to the lab
        lab = Lab.objects.get(id=lab_id)
        user = User.objects.get(id=lab.user_id)
        appointment = Appointment.objects.create(lab=lab, service_name=service_name, date=date)
        notification_message = f'New request for {service_name} on {date}'
        notification = Notification.objects.create(
            notification_lab=lab,
            notification_user=user,
            notification_appointment=appointment,
            message=notification_message,
            is_confirmed=False,
            is_declined=False
        )

        channel.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        self.channel.start_consuming()


consumer = RequestConsumer()

class AppointmentUpdatesConsumer:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(settings.RABBITMQ_HOST)
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='appointment_updates')
        self.channel.basic_consume(
            queue='appointment_updates', on_message_callback=self.callback, auto_ack=True
        )

    def start(self):
        print('Appointment updates consumer started...')
        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        print('Received appointment update:', body)
        appointment_id = body.split(': ')[1]
        appointment = Appointment.objects.get(pk=appointment_id)
        # Send notification to the user
        notification_message = f'Appointment request updated, please confirm or decline: {appointment}'
        notification = Notification.objects.create(

            notification_lab=appointment.lab_appointment,
            notification_user=appointment.patient,
            notification_appointment=appointment,
            message=notification_message,
            is_confirmed=False,
            is_declined=False
        )
        print(f'Notification sent to {appointment.patient.email}')


if __name__ == '__main__': # check this part
    consumer = AppointmentUpdatesConsumer()
    consumer.start()
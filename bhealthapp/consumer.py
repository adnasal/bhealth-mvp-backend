import json

import pika
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from bhealthapp.models import Lab, User
from bhealthapp.models import Notification, Appointment


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
                notification_appointment=appointments[0],
                message=notification_message,
                is_confirmed=True,
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
            notification_appointment=appointment,
            message=notification_message,
            is_confirmed=False,
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
            notification_appointment=appointment,
            message=notification_message,
            is_confirmed=False,
        )
        print(f'Notification sent to {appointment.patient.email}')


if __name__ == '__main__':  # check this part
    consumer = AppointmentUpdatesConsumer()
    consumer.start()


class AppointmentConsumer:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue='appointment')

        self.channel.basic_consume(queue='appointment', on_message_callback=self.callback, auto_ack=True)

    def callback(self, ch, method, properties, body):
        message = body.decode('utf-8')

        # Get the appointment related to the message
        appointment = Appointment.objects.filter(status=1).latest('date')

        # Send notifications to both the user and the lab
        self.send_notification(appointment.patient, appointment.lab_appointment, appointment)
        self.send_notification(appointment.lab_appointment.user, appointment.lab_appointment, appointment)

    def send_notification(self, user, lab, appointment):
        # Create the notification
        notification = Notification.objects.create(
            notification_appointment=appointment,
            message='New appointment has been added.'
        )

        # Send email notification to the user
        user_message = render_to_string('appointment_notification.html', {'appointment': appointment})
        send_mail(
            'New Appointment Notification',
            user_message,
            settings.EMAIL_HOST_USER,
            [user.email],
            html_message=user_message,
        )

    def start(self):
        self.channel.start_consuming()

    def stop(self):
        self.channel.stop_consuming()
        self.connection.close()


consumer = AppointmentConsumer()
consumer.start()


class NotificationConsumer:  # CHANGE NAME TO CANCEL APP
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=settings.RABBITMQ_QUEUE)

    def start_consuming(self):
        self.channel.basic_consume(queue=settings.RABBITMQ_QUEUE, on_message_callback=self.callback, auto_ack=True)
        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        appointment_id = int(body)
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            user = appointment.patient
            lab = appointment.lab_appointment
            notification = Notification.objects.create(
                notification_appointment=appointment,
                message='Your appointment has been canceled.')
            notification.save()
        except Appointment.DoesNotExist:
            pass

    def stop_consuming(self):
        self.channel.stop_consuming()
        self.connection.close()


class Command(BaseCommand):
    help = 'Starts the notification consumer.'

    def handle(self, *args, **options):
        consumer = NotificationConsumer()
        try:
            consumer.start_consuming()
        except KeyboardInterrupt:
            consumer.stop_consuming()

import json
from datetime import datetime

import pika
from django.core.exceptions import ObjectDoesNotExist

from bhealthapp.models import Appointment, Notification, Lab
from rmq_send_message import json_string_to_dict


class Consumer:

    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        self.channel = self.connection.channel()
        self.channel.basic_consume(queue='results', on_message_callback=self.result_added)
        self.channel.basic_consume(queue='requests', on_message_callback=self.process_request)
        self.channel.basic_consume(queue='appointment_updates', on_message_callback=self.process_appointment)
        self.channel.basic_consume(queue='appointment', on_message_callback=self.notification_confirmed)
        self.channel.basic_consume(queue='appointment_canceled', on_message_callback=self.cancel_appointment)

    def result_added(self, channel, method, properties, body):
        try:
            appointment_id = json_string_to_dict(body).get('appointment_id')
            appointment = Appointment.objects.get(id=appointment_id)

            notification_message = f'Result added for appointment {appointment_id}'

            Notification.objects.create(
                notification_appointment=appointment,
                message=notification_message,
                is_confirmed=True,
                notification_date=datetime.now()
            )
        except Appointment.DoesNotExist:

            notification_message = f'Result added for non-existent appointment with ID {appointment_id}'

            Notification.objects.create(
                message=notification_message,
                is_confirmed=True,
                notification_date=datetime.now()
            )
        finally:

            channel.basic_ack(delivery_tag=method.delivery_tag)

    def process_request(self, channel, method, properties, body):
        try:

            appointment_id = json_string_to_dict(body).get('appointment_id')
            appointment = Appointment.objects.get(pk=appointment_id)

            notification_message = f'New request for appointment with id {appointment_id} has been made.'
            Notification.objects.create(
                notification_appointment=appointment,
                message=notification_message,
                is_confirmed=False,
                notification_date=datetime.now()
            )

        except (KeyError, json.decoder.JSONDecodeError, ValueError) as e:
            error_message = str(e)
            Notification.objects.create(message=error_message)
            channel.basic_nack(delivery_tag=method.delivery_tag)

        except Exception as e:
            error_message = f"An error occurred while processing the request: {str(e)}"
            Notification.objects.create(message=error_message, notification_date=datetime.now())
            channel.basic_nack(delivery_tag=method.delivery_tag)

        else:
            channel.basic_ack(delivery_tag=method.delivery_tag)

    def process_appointment(self, channel, method, properties, body):
        try:
            appointment_id = json_string_to_dict(body).get('appointment_id')
            appointment = Appointment.objects.get(pk=appointment_id)
            notification_message = f'Appointment request updated, please confirm or decline: {appointment}'
            Notification.objects.create(
                notification_appointment=appointment,
                message=notification_message,
                is_confirmed=False,
                notification_date=datetime.now()
            )
        except (Appointment.DoesNotExist, KeyError, TypeError) as e:
            print(f"Appointment with id {appointment_id} does not exist.")
            self.channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        except Exception as e:
            print(f"Unknown error processing appointment: {e}")
            self.channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        finally:
            channel.basic_ack(delivery_tag=method.delivery_tag)

    def notification_confirmed(self, ch, method, properties, body):
        try:

            appointment_id = json_string_to_dict(body).get('appointment_id')
            appointment = Appointment.objects.get(id=appointment_id)

            Notification.objects.create(
                notification_appointment=appointment,
                message='New appointment has been confirmed.',
                notification_date=datetime.now()
            )
        except Appointment.DoesNotExist:
            print("Error: The appointment does not exist")
            self.channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        except Lab.DoesNotExist:
            print("Error: The lab does not exist")
            self.channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        except Exception as e:
            print("Error: ", str(e))
            self.channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        finally:
            self.channel.basic_ack(delivery_tag=method.delivery_tag)

    def cancel_appointment(self, ch, method, properties, body):
        try:
            appointment_id = json_string_to_dict(body).get('appointment_id')
            appointment = Appointment.objects.get(id=appointment_id)

            notification = Notification.objects.create(
                notification_appointment=appointment,
                message='Your appointment has been canceled.',
                notification_date=datetime.now())
            notification.save()

        except ObjectDoesNotExist as e:
            print(f"Appointment with id {appointment_id} does not exist.")
            self.channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        except ValueError as e:
            print(f"Invalid appointment id {body}.")
            self.channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        except Exception as e:
            print(f"An error occurred while canceling appointment: {str(e)}")
            self.channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        finally:
            self.channel.basic_ack(delivery_tag=method.delivery_tag)

    def start(self):
        self.channel.start_consuming()

import json

import pika
from django.conf import settings

def get_rabbitmq_connection():
    credentials = pika.PlainCredentials(
        username=settings.RABBITMQ_USER,
        password=settings.RABBITMQ_PASSWORD
    )
    parameters = pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        virtual_host=settings.RABBITMQ_VHOST,
        credentials=credentials
    )
    connection = pika.BlockingConnection(parameters)
    return connection

def get_rabbitmq_channel():
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    channel.exchange_declare(
        exchange=settings.RABBITMQ_EXCHANGE,
        exchange_type='topic',
        durable=True
    )
    return channel
# koristi gdje ti treba
def publish_message():
    channel = get_rabbitmq_channel()
    message = {'data': 'my message'}
    channel.basic_publish(
        exchange=settings.RABBITMQ_EXCHANGE,
        routing_key='my_routing_key',
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2
        )
    )
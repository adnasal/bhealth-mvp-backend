import json

import pika


def send_messages(queue_name: str, message: dict) -> None:
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)

    message = dict_to_json_string(message)

    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
        ))

    connection.close()


def dict_to_json_string(payload: dict) -> str:
    return json.dumps(payload)


def json_string_to_dict(payload: str) -> dict:
    return json.loads(payload)

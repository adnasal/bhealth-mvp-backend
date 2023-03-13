import pika
import json
from django.core.serializers import serialize

# Establish a connection to the RabbitMQ server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672))

# Create a channel on the connection
channel = connection.channel()

# Declare a queue to send messages to
channel.queue_declare(queue='hello')

# Publish a message to the queue
channel.basic_publish(exchange='', routing_key='hello', body='Hello, world!')

# Close the connection to the RabbitMQ server
connection.close()


#from bhealthapp.models import Appointment
#from django.conf import settings


#app = Appointment.objects.get(pk=10)

#settings.configure()

#message = {
 #   'type': 'result_created',
  #  'data': serialize('json', [app])
#}
#connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672))
#channel = connection.channel()

#channel.queue_declare(queue='notifications')
#channel.basic_publish(exchange='', routing_key='notifications', body=json.dumps(message))

#connection.close()
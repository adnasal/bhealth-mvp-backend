import pika

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
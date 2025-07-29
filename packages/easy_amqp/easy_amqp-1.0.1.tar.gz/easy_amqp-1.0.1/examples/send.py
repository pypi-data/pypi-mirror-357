import pika
import json

credentials = pika.PlainCredentials('test', 'test')
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=credentials))
channel = connection.channel()

test_value = "test"
for counter in range(10):
    channel.basic_publish(exchange='',
                        routing_key=test_value,
                        body=f"{test_value} {counter}")

connection.close()
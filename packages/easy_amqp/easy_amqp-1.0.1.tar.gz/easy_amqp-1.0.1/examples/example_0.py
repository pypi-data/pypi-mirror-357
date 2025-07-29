import pika.channel
from easy_amqp import EasyAMQP
from easy_amqp.models import Message
from pika.connection import ConnectionParameters

import pika

"""
This example shows how to use the listen to the queue "test" to consume messages.
The listen decorator will consume messages one by one and pass them to the consumer function."""

credentials = pika.PlainCredentials('test', 'test')
connection_params = ConnectionParameters("localhost", credentials=credentials)

rabbit = EasyAMQP(connection_parameters=connection_params)

@rabbit.listen("test", message_type=str)
def consume(message: Message, channel: pika.channel.Channel):
    print(message.body) # will be a str due to the message_type parameter


rabbit.run()
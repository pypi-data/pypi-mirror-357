import pika.channel
from easy_amqp import EasyAMQP
from easy_amqp.models import Message, Retry

import pika

"""
This example shows how to use multiple connection parameters and how to set a retry policy if the connection fails.
"""

rabbit = EasyAMQP(connection_parameters=[
    pika.ConnectionParameters('rabbitmq1'),
    pika.ConnectionParameters('rabbitmq2'),
], retry=Retry(3, 5.0))

@rabbit.listen("test", message_type=str)
def consume(message: Message, channel: pika.channel.Channel):
    print(message.body) # will be a str due to the message_type parameter


rabbit.run()
import pika.channel
from easy_amqp import EasyAMQP
from easy_amqp.models import Message
from pika.connection import ConnectionParameters

import pika

"""
This example shows how to use a custom parser function to convert the message body from bytes to a custom object."""

credentials = pika.PlainCredentials('test', 'test')
connection_params = ConnectionParameters("localhost", credentials=credentials)

rabbit = EasyAMQP(connection_parameters=connection_params)

class Data:
    def __init__(self, value: str):
        self.value = value



def custom_parser(body: bytes) -> Data:
    """
    Custom parser function to convert bytes to str.
    This is useful if you want to handle the message body in a specific way.
    """
    return Data(body.decode('utf-8'))

@rabbit.listen("test", message_type=Data, custom_parser=custom_parser)
def consume(message: Message, channel: pika.channel.Channel):
    print(message.body.value)


rabbit.run()
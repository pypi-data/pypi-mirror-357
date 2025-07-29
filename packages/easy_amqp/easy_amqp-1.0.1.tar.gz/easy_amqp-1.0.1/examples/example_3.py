import pika.channel
import pika.connection
import pika.exceptions
from easy_amqp import EasyAMQP
from easy_amqp.models import Message
from pika.connection import ConnectionParameters
from typing import Union
import pika


def on_connection_open(connection: pika.connection.Connection):
    print("Connection opened successfully")

def on_connection_error(connection: pika.connection.Connection, exception: Union[str, Exception]):
    print(f"Connection error: {exception}")

def on_channel_closed(channel: pika.channel.Channel, exception: pika.exceptions.ChannelClosed):
    print(f"Channel: {channel} closed unexpectedly reason: {exception}")

credentials = pika.PlainCredentials('test', 'test')
connection_params = ConnectionParameters("localhost", credentials=credentials)

rabbit = EasyAMQP(connection_parameters=connection_params, on_connection_open=on_connection_open, on_connection_error=on_connection_error, on_channel_closed=on_channel_closed)



@rabbit.listen("test", message_type=str)
def consume(message: Message, channel: pika.channel.Channel):
    print(message.body) # will be a str due to the message_type parameter


rabbit.run()
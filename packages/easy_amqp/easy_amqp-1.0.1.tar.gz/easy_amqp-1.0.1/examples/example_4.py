from easy_amqp import EasyAMQP
from pika.connection import ConnectionParameters
import pika
from easy_amqp.models import Queue, Exchange, ExchangeType


credentials = pika.PlainCredentials('test', 'test')
connection_params = ConnectionParameters("localhost", credentials=credentials)

rabbit = EasyAMQP(connection_parameters=connection_params)

"""
This example shows how to use the EasyAMQP library to create a queue and an exchange without using decorators, 
and then run the RabbitMQ server.
"""


rabbit.add_queue(Queue(
    name="test_queue",
    passive=True,
    durable=True,
    exclusive=True,
    auto_delete=True,
    arguments=None,
    dead_letter_queue=None,
))

exchange: Exchange = Exchange(
        name="test_exchange",
        type=ExchangeType.fanout,
        durable=True,
        passive=False,
        internal=False,
        auto_delete=False,
        arguments=None
    )
rabbit.add_exchange(exchange)

rabbit.run()
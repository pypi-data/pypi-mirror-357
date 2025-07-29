import pika.channel
from easy_amqp import EasyAMQP
from easy_amqp.models import Message, ExchangeType
from pika.connection import ConnectionParameters

import pika

credentials = pika.PlainCredentials('test', 'test')
connection_params = ConnectionParameters("localhost", credentials=credentials)

rabbit = EasyAMQP(connection_parameters=connection_params)



@rabbit.declare_queue("test_queue") # will declare a queue named "test_queue"
@rabbit.declare_exchange("test_exchange", exchange_type=ExchangeType.direct) # will declare an exchange named "test_exchange" of type direct
@rabbit.bind(exchange="test_exchange", queue="test_queue", routing_key="test_routing_key") # exchange will send messages to the queue with the routing key "test_routing_key"
@rabbit.listen("test_queue", message_type=str) # will listen to the queue "test_queue" and consume messages as strings
@rabbit.batch()
def consume(message: Message, channel: pika.channel.Channel):
    print(message.body) # will be a List[str] due to the batch decorator


rabbit.run()
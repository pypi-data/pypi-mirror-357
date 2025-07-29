import pika.channel
import pika
import pytest
from easy_amqp.EasyAMQP import EasyAMQP
from easy_amqp.models import Message
from typing import List, Dict, Any


def test_consuming(
    rabbitmq_container: Dict[str, Any],
    easy_amqp: EasyAMQP
) -> None:
    """
    Tests a basic message consumption scenario.
    """
    result: Dict[str, Any] = {}
    queue_name: str = "test_queue"
    exchange_name: str = "test_exchange"
    message: str = "Test message"

    # Setup RabbitMQ with a blocking connection to publish a message
    connection: pika.BlockingConnection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=rabbitmq_container["host"],
            credentials=pika.PlainCredentials("guest", "guest"),
            port=rabbitmq_container["client_port"]
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=queue_name) # type: ignore
    channel.exchange_declare(exchange=exchange_name, exchange_type='direct') # type: ignore
    channel.queue_bind(queue=queue_name, exchange=exchange_name, routing_key="test_routing_key") # type: ignore
    channel.basic_publish(exchange=exchange_name, routing_key="test_routing_key", body=message.encode('utf-8'))
    connection.close()

    @easy_amqp.listen(queue_name, message_type=str)
    def consuming(msg: Message, _: pika.channel.Channel) -> None: # type: ignore
        result['message'] = msg.body
        easy_amqp.stop()

    easy_amqp.run()

    if 'message' not in result:
        pytest.fail("Consumption callback was not called")
    assert result['message'] == message


def test_consuming_batch(
    rabbitmq_container: Dict[str, Any],
    easy_amqp: EasyAMQP
) -> None:
    """
    Tests consuming multiple messages in a batch.
    """
    result: Dict[str, Any] = {}
    queue_name = "test_queue"
    exchange_name = "test_exchange"
    message_prefix = "Test message"

    # Setup RabbitMQ with a blocking connection to publish multiple messages
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=rabbitmq_container["host"],
            credentials=pika.PlainCredentials("guest", "guest"),
            port=rabbitmq_container["client_port"]
        )
    )
    channel = connection.channel() # type: ignore
    channel.queue_declare(queue=queue_name) # type: ignore
    channel.exchange_declare(exchange=exchange_name, exchange_type='direct') # type: ignore
    channel.queue_bind(queue=queue_name, exchange=exchange_name, routing_key="test_routing_key") # type: ignore
    for counter in range(5):
        channel.basic_publish(exchange=exchange_name, routing_key="test_routing_key", body=f"{message_prefix} {counter}".encode('utf-8'))
    connection.close()

    @easy_amqp.listen(queue_name, message_type=str)
    @easy_amqp.batch()
    def consuming(msgs: List[Message], _: pika.channel.Channel) -> None: # type: ignore
        result['messages'] = msgs
        easy_amqp.stop()

    easy_amqp.run()

    if 'messages' not in result:
        pytest.fail("Consumption callback was not called")

    assert isinstance(result['messages'], list)
    assert len(result['messages']) == 5 # type: ignore
    for i, msg in enumerate(result['messages']): # type: ignore
        assert msg.body == f"{message_prefix} {i}" # type: ignore
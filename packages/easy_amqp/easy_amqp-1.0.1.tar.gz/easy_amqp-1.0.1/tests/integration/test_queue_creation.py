import pika.channel
import pika.exceptions
import pika
import pytest
from ..conftest import get_queue_properties
from easy_amqp.EasyAMQP import EasyAMQP
from easy_amqp.models import Queue, Message, DeadLetterQueue
from typing import Dict, Any, Union



def test_add_queue(
    rabbitmq_container: Dict[str, Any],
    easy_amqp: EasyAMQP
) -> None:
    """
    Tests the creation of a queue using EasyAMQP.
    """
    result: Dict[str, Any] = {}

    def on_queue_declared(_: pika.channel.Channel, q: Queue) -> None:
        result['queue'] = get_queue_properties(rabbitmq_container["host"], rabbitmq_container["api_port"], q.name)
        easy_amqp.stop()

    queue = Queue(
        name="test_queue",
        passive=False,
        durable=True,
        exclusive=True,
        auto_delete=True,
        arguments=None,
        dead_letter_queue=None,
        on_queue_declared=on_queue_declared
    )
    easy_amqp.add_queue(queue)
    easy_amqp.run()

    if 'queue' not in result:
        pytest.fail("Queue declaration callback was not called")

    assert result['queue']['name'] == queue.name
    # assert result['queue']['durable'] is True #ToDo check why this is not working
    assert result['queue']['auto_delete'] == queue.auto_delete
    assert result['queue']['arguments'] == {}
    assert result['queue']['exclusive'] is queue.exclusive


def test_add_queue_with_decorator(
    rabbitmq_container: Dict[str, Any],
    easy_amqp: EasyAMQP
) -> None:
    """
    Tests the creation of a queue using the EasyAMQP decorator.
    """
    result: Dict[str, Any] = {}
    queue_name: str = "test_queue"

    def on_queue_declared(_: pika.channel.Channel, q: Queue) -> None:
        result['queue'] = get_queue_properties(rabbitmq_container["host"], rabbitmq_container["api_port"], q.name)
        easy_amqp.stop()

    @easy_amqp.declare_queue(queue_name, on_queue_declared=on_queue_declared)
    def consuming(msg: Message, _: pika.channel.Channel) -> None: # type: ignore
        pass

    easy_amqp.run()

    if 'queue' not in result:
        pytest.fail("Queue declaration callback was not called")
    assert result['queue']['name'] == queue_name


def test_add_queue_passive_mode_queue_does_not_exists(
    rabbitmq_container: Dict[str, Any],
) -> None:
    """
    Tests adding a queue in passive mode when the queue does not exist.
    Expects a ChannelClosedByBroker exception.
    """
    result: Dict[str, Any] = {'ok': False}

    def channel_closed(_: pika.channel.Channel, exception: pika.exceptions.ChannelClosed) -> None:
        result['ok'] = isinstance(exception, pika.exceptions.ChannelClosedByBroker) and "NOT_FOUND" in str(exception)
        easy_rabbit.stop() # Stop this specific instance

    # Should not go to this callback because passive=True will cause the broker to close the channel automatically
    def on_queue_declared(_: pika.channel.Channel, q: Queue) -> None:
        easy_rabbit.stop() # Stop this specific instance

    # Create a new EasyAMQP instance for this specific test case,
    # as its behavior (on_channel_closed) is unique.
    credentials = pika.PlainCredentials("guest", "guest")
    connection_params = pika.ConnectionParameters(
        host=rabbitmq_container["host"],
        credentials=credentials,
        port=rabbitmq_container["client_port"]
    )
    easy_rabbit = EasyAMQP(connection_params, on_channel_closed=channel_closed)

    easy_rabbit.add_queue(Queue(
        name="test_queue",
        passive=True,
        durable=True,
        exclusive=True,
        auto_delete=True,
        arguments=None,
        dead_letter_queue=None,
        on_queue_declared=on_queue_declared
    ))
    easy_rabbit.run()

    assert result['ok'], "Expected channel to be closed with a 'no queue' error, but it was not."



def setup_rabbit_with_queue(rabbitmq_container: Dict[str, Any], queue: str) -> None:
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=rabbitmq_container["host"],
            credentials=pika.PlainCredentials("guest", "guest"),
            port=rabbitmq_container["client_port"]
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=queue) # type: ignore
    connection.close()


def test_add_queue_passive_mode_queue_exists(
    rabbitmq_container: Dict[str, Any],
) -> None:
    """
    Tests adding a queue in passive mode when the queue already exists.
    """
    result: Dict[str, Any] = {'ok': False}

    # Declare the queue manually before EasyAMQP attempts to declare it passively
    setup_rabbit_with_queue(rabbitmq_container, "test_queue")
    def channel_closed(_: pika.channel.Channel, reason: Union[pika.exceptions.ChannelClosed, str]) -> None:
        result['ok'] = False
        easy_rabbit.stop() # Stop this specific instance

    def on_queue_declared(_: pika.channel.Channel, q: Queue) -> None:
        queue_properties: Dict[str, Any] = get_queue_properties(rabbitmq_container["host"], rabbitmq_container["api_port"], q.name)
        result['ok'] = queue_properties['name'] == "test_queue"
        easy_rabbit.stop() # Stop this specific instance

    # Create a new EasyAMQP instance for this specific test case,
    # as its behavior (on_channel_closed) is unique.
    credentials = pika.PlainCredentials("guest", "guest")
    connection_params = pika.ConnectionParameters(
        host=rabbitmq_container["host"],
        credentials=credentials,
        port=rabbitmq_container["client_port"]
    )
    easy_rabbit: EasyAMQP = EasyAMQP(connection_params, on_channel_closed=channel_closed)

    easy_rabbit.add_queue(Queue(
        name="test_queue",
        passive=True,
        durable=True,
        exclusive=True,
        auto_delete=True,
        arguments=None,
        dead_letter_queue=None,
        on_queue_declared=on_queue_declared
    ))
    easy_rabbit.run()
    assert result['ok']


def test_add_queue_with_dead_letter(
    rabbitmq_container: Dict[str, Any],
    easy_amqp: EasyAMQP
) -> None:
    """
    Tests the creation of a queue with dead-letter queue arguments.
    """
    result: Dict[str, Any] = {}

    def on_queue_declared(_: pika.channel.Channel, q: Queue) -> None:
        result['queue'] = get_queue_properties(rabbitmq_container["host"], rabbitmq_container["api_port"], q.name)
        easy_amqp.stop()

    dlq = DeadLetterQueue(
        x_dead_letter_exchange="dlx_exchange",
        x_dead_letter_routing_key="dlx_routing_key",
        x_max_length=100,
        x_message_ttl=60000
    )
    easy_amqp.add_queue(Queue(
        name="test_queue",
        passive=False,
        durable=False,
        exclusive=False,
        auto_delete=False,
        arguments=None,
        dead_letter_queue=dlq,
        on_queue_declared=on_queue_declared
    ))
    easy_amqp.run()

    if 'queue' not in result:
        pytest.fail("Queue declaration callback was not called")

    assert result['queue']['arguments'] == {
        'x-dead-letter-exchange': dlq.x_dead_letter_exchange,
        'x-dead-letter-routing-key': dlq.x_dead_letter_routing_key,
        'x-max-length': dlq.x_max_length,
        'x-message-ttl': dlq.x_message_ttl
    }


def test_add_queue_with_dlq_and_arguments(
    rabbitmq_container: Dict[str, Any],
    easy_amqp: EasyAMQP
) -> None:
    """
    Tests the creation of a queue with dead-letter queue arguments and additional custom arguments.
    """
    result: Dict[str, Any] = {}

    def on_queue_declared(_: pika.channel.Channel, q: Queue) -> None:
        result['queue'] = get_queue_properties(rabbitmq_container["host"], rabbitmq_container["api_port"], q.name)
        easy_amqp.stop()

    dlq = DeadLetterQueue(
        x_dead_letter_exchange="dlx_exchange",
        x_dead_letter_routing_key="dlx_routing_key",
        x_max_length=100,
        x_message_ttl=60000
    )
    easy_amqp.add_queue(Queue(
        name="test_queue",
        passive=False,
        durable=False,
        exclusive=False,
        auto_delete=False,
        arguments={'x-queue-mode': 'lazy'},
        dead_letter_queue=dlq,
        on_queue_declared=on_queue_declared
    ))
    easy_amqp.run()

    if 'queue' not in result:
        pytest.fail("Queue declaration callback was not called")

    assert result['queue']['arguments'] == {
        'x-dead-letter-exchange': dlq.x_dead_letter_exchange,
        'x-dead-letter-routing-key': dlq.x_dead_letter_routing_key,
        'x-max-length': dlq.x_max_length,
        'x-message-ttl': dlq.x_message_ttl,
        'x-queue-mode': 'lazy'
    }
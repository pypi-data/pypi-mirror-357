import pika.channel
import pytest
from ..conftest import get_exchange_properties
from easy_amqp.EasyAMQP import EasyAMQP
from easy_amqp.models import Exchange, ExchangeType, Message
from typing import Dict, Any

def test_add_exchange(
    rabbitmq_container: Dict[str, Any],
    easy_amqp: EasyAMQP
) -> None:
    """
    Tests the creation of an exchange using EasyAMQP.
    """
    result: Dict[str, Any] = {}

    def on_exchange_declared(_: pika.channel.Channel, e: Exchange) -> None:
        result['exchange'] = get_exchange_properties(rabbitmq_container["host"], rabbitmq_container["api_port"], e.name)
        easy_amqp.stop()

    exchange: Exchange = Exchange(
        name="test_exchange",
        type=ExchangeType.fanout,
        durable=True,
        passive=False,
        internal=False,
        auto_delete=False,
        arguments=None,
        on_exchange_declared=on_exchange_declared
    )
    easy_amqp.add_exchange(exchange)
    easy_amqp.run()

    if 'exchange' not in result:
        pytest.fail("Exchange declaration callback was not called")

    assert result['exchange']['name'] == exchange.name
    assert result['exchange']['durable'] is True #ToDo check why this is not working
    assert result['exchange']['auto_delete'] == exchange.auto_delete
    assert result['exchange']['arguments'] == {}


def test_add_exchange_with_decorator(
    rabbitmq_container: Dict[str, Any],
    easy_amqp: EasyAMQP
) -> None:
    """
    Tests the creation of an exchange using the EasyAMQP decorator.
    """
    result: Dict[str, Any] = {}
    exchange_name: str = "test_exchange"

    def on_exchange_declared(_: pika.channel.Channel, e: Exchange) -> None:
        result['exchange'] = get_exchange_properties(rabbitmq_container["host"], rabbitmq_container["api_port"], e.name)
        easy_amqp.stop()

    @easy_amqp.declare_exchange(exchange=exchange_name, exchange_type=ExchangeType.fanout, on_exchange_declared=on_exchange_declared)
    def consuming(msg: Message, channel: pika.channel.Channel) -> None: # type: ignore
        pass

    easy_amqp.run()

    if 'exchange' not in result:
        pytest.fail("Exchange declaration callback was not called")
    assert result['exchange']['name'] == exchange_name
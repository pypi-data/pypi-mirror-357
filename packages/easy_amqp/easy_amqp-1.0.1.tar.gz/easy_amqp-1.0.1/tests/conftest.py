import pika
import pytest
import requests
from testcontainers.rabbitmq import RabbitMqContainer
from easy_amqp.EasyAMQP import EasyAMQP

from typing import Dict, Any, Iterator



@pytest.fixture
def rabbitmq_container() -> Iterator[Dict[str, Any]]:
    """
    Pytest fixture to set up and tear down a RabbitMQ container for the entire test session.
    Yields a dictionary containing host, client_port, and api_port.
    """
    port_client: int = 5672
    port_api: int = 15672
    with RabbitMqContainer("rabbitmq:3.12-management").with_exposed_ports(port_client, port_api) as container:
        host: str = container.get_container_host_ip()
        client_port: int = container.get_exposed_port(port_client)
        api_port: int = container.get_exposed_port(port_api)
        yield {"host": host, "client_port": client_port, "api_port": api_port}

@pytest.fixture
def easy_amqp(rabbitmq_container: Dict[str, Any]) -> Iterator[EasyAMQP]:
    """
    Pytest fixture to provide an EasyAMQP instance, depending on the RabbitMQ container.
    A new instance is provided for each test function.
    """
    credentials = pika.PlainCredentials("guest", "guest")
    connection_params = pika.ConnectionParameters(
        host=rabbitmq_container["host"],
        credentials=credentials,
        port=rabbitmq_container["client_port"]
    )
    easy_rabbit: EasyAMQP = EasyAMQP(connection_params)
    yield easy_rabbit
    # Ensure easy_rabbit is stopped after each test using this fixture
    easy_rabbit.stop()


def get_exchange_properties(host: str, port_api: int, exchange_name: str) -> Dict[str, Any]:
    """
    Retrieves exchange properties from the RabbitMQ management API.
    """
    url = f"http://{host}:{port_api}/api/exchanges/%2F/{exchange_name}"
    response = requests.get(url, auth=("guest", "guest"))
    response.raise_for_status()
    return response.json()

def get_queue_properties(host: str, port_api: int, queue_name: str) -> Dict[str, Any]:
    """
    Retrieves queue properties from the RabbitMQ management API.
    """
    url = f"http://{host}:{port_api}/api/queues/%2F/{queue_name}"
    response = requests.get(url, auth=("guest", "guest"))
    response.raise_for_status()
    return response.json()


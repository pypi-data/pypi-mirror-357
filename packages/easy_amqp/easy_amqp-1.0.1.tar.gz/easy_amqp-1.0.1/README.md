# EasyAMQP

---

EasyAMQP is a Python library built on top of `pika` that simplifies interacting with RabbitMQ. It provides a decorator-based approach for declaring queues, exchanges, bindings, and setting up message listeners, aiming to reduce boilerplate code and improve readability. You can find some examples in 
`/examples`

## Features

* **Simplified Connection Management**: Handles connections and reconnections to RabbitMQ.
* **Decorator-based Topology Definition**: Easily declare queues, exchanges, and bindings using decorators.
* **Listener Management**: Define message consumers with automatic message parsing and acknowledgment.
* **Batch Consumption**: Support for processing messages in batches.
* **Dead Letter Queues**: Configure dead-lettering for queues directly.
* **Prefetch Control**: Set QoS prefetch settings for consumers.
* **Flexible Deployment**: Run your AMQP operations in a separate thread or in the main thread.

---

## Installation

```bash
pip install easy-amqp
```

## Usage

### Basic consuming

```python
import pika
from easy_amqp import EasyAMQP

# Single connection parameter
amqp = EasyAMQP(pika.ConnectionParameters('localhost'))

 # the consumer will always receive a Message object provided by the library. The message object has the property body which will be the object given in message_type. you can add a custom parser by setting the  parameter custom_parser
@amqp.listen(queue='my_queue', message_type=str)
def process_message(message: Message):
    print(f"Received message: {message.body}")

amqp.run()
#or run in thread
thread = amqp.run_in_thread()

```

### Basic Setup and Connection

To get started, instantiate EasyAMQP with your RabbitMQ connection parameters.

```python
import pika
from easy_amqp import EasyAMQP

# Single connection parameter
amqp = EasyAMQP(pika.ConnectionParameters('localhost'))



# or use multiple connection parameters for high availability
amqp_ha = EasyAMQP([
    pika.ConnectionParameters('rabbitmq1'),
    pika.ConnectionParameters('rabbitmq2'),
])

# use retry mechanism in case of connection errors
amqp_robust = EasyAMQP(
    pika.ConnectionParameters('localhost'),
    retry=Retry(max_retries=5, initial_delay=1.0)
)

# with connection callbacks and retry
def on_connection_open(connection: pika.connection.Connection):
    print(f"Connection opened: {connection}")

def on_connection_error(connection: pika.connection.Connection, error: Union[str, Exception]):
    print(f"Connection error: {error}")

amqp_connection_callback = EasyAMQP(
    pika.ConnectionParameters('localhost'),
    retry=Retry(max_retries=5, initial_delay=1.0),
    on_connection_open=on_connection_open,
    on_connection_error=on_connection_error
)

amqp.run()
```

### Declare by decorators

```python
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

```


### Declare by manually

```python
from easy_amqp import EasyAMQP
from easy_amqp.models import Message, ExchangeType, Exchange, Queue, Binding
from pika.connection import ConnectionParameters

import pika

credentials = pika.PlainCredentials('test', 'test')
connection_params = ConnectionParameters("localhost", credentials=credentials)

rabbit = EasyAMQP(connection_parameters=connection_params)

rabbit.add_exchange(Exchange(...)) # replace ... with correct values
rabbit.add_queue(Queue(...))  # replace ... with correct values
rabbit.add_binding(Binding(...)) # replace ... with correct values



@rabbit.listen("test_queue", message_type=str) # will listen to the queue "test_queue" and consume messages as strings
def consume(message: Message, channel: pika.channel.Channel):
    print(message.body) # will be a List[str] due to the batch decorator


rabbit.run()

```



## Decorator Reference

| Decorator               | Description                                         | Key Arguments                                                                                   |
|-------------------------|-----------------------------------------------------|--------------------------------------------------------------------------------------------------|
| `@declare_queue(...)`   | Declares a RabbitMQ queue                           | `queue`, `durable`, `exclusive`, `auto_delete`, `arguments`                                     |
| `@declare_exchange(...)`| Declares a RabbitMQ exchange                        | `exchange`, `exchange_type`, `durable`, `auto_delete`, `internal`, `arguments`                  |
| `@bind(...)`            | Binds a queue to an exchange                        | `exchange`, `queue`, `routing_key`, `arguments`                                                  |
| `@prefetch(...)`        | Configures prefetch (QoS) settings for the consumer | `prefetch_count`, `prefetch_size`, `global_qos`                                                  |
| `@dead_letter(...)`     | Sets dead-letter queue parameters on a queue        | `x_dead_letter_exchange`, `x_dead_letter_routing_key`, `x_max_length`, `x_message_ttl`          |
| `@batch(...)`           | Enables batch processing of messages                | `batch_time`                                                                                     |
| `@listen(...)`          | Subscribes a function to a queue                    | `queue`, `message_type`, `auto_ack`, `exclusive`, `consumer_tag`, `custom_parser`               |
| `@listen_batch(...)`    | Like `@listen`, but with batch support              | `queue`, `message_type`, `batch_time`, `auto_ack`, `exclusive`, `consumer_tag`, `custom_parser` |

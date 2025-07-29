import pika
import pika.channel

import pika.spec
from typing import Callable, List, Dict, Optional, Type, TypeVar, Any
from dataclasses import dataclass, field
from enum import StrEnum

T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])

@dataclass
class Retry:
    retries: int
    delay: float

@dataclass
class DeadLetterQueue:
    x_dead_letter_exchange: str
    x_dead_letter_routing_key: str
    x_max_length: Optional[int] = None
    x_message_ttl:  Optional[int] = None

    def to_args(self) -> Dict[str, Any]:
        args: Dict[str, Any] = {}
        if self.x_max_length:
            args['x-max-length'] = int(self.x_max_length)
        if self.x_message_ttl:
            args['x-message-ttl'] = int(self.x_message_ttl)
        args['x-dead-letter-exchange'] = self.x_dead_letter_exchange
        args['x-dead-letter-routing-key'] = self.x_dead_letter_routing_key
        return args

@dataclass
class Queue:
    name: str
    passive: bool
    durable: bool
    exclusive: bool
    auto_delete: bool
    arguments: Optional[Dict[str, Any]]
    dead_letter_queue: Optional[DeadLetterQueue]
    on_queue_declared: Optional[Callable[[pika.channel.Channel, 'Queue'], None]] = None


class ExchangeType(StrEnum):
    direct = 'direct'
    fanout = 'fanout'
    headers = 'headers'
    topic = 'topic'


@dataclass
class Exchange:
    name: str
    type: ExchangeType
    durable: bool
    passive: bool
    auto_delete: bool
    internal: bool
    arguments: Optional[Dict[str, Any]]
    on_exchange_declared: Optional[Callable[[pika.channel.Channel, 'Exchange'], None]] = None


@dataclass
class Binding:
    exchange: str
    routing_key: str
    queue: str
    arguments: Optional[Dict[str, Any]]
    on_binding_declared: Optional[Callable[[pika.channel.Channel, 'Binding'], None]] = None


@dataclass
class Message:
    body: T
    method: pika.spec.Basic.Deliver
    props: pika.spec.BasicProperties


@dataclass
class Batch:
    batch_time: float
    scheduled: bool
    items: List[Message] = field(default_factory=list)


@dataclass
class Listener:
    queue: str
    func: Callable[..., None] 
    message_type: Type[T]
    auto_ack: bool
    exclusive: bool
    consumer_tag: Optional[str]
    arguments: Optional[Dict[str, Any]]
    parser: Optional[Callable[[bytes], T]]
    on_channel_open: Optional[Callable[[pika.channel.Channel], None]]


@dataclass
class Prefetch:
    size: int = 0
    count: int = 0
    global_qos: bool = False


@dataclass
class Handler:
    listener: Listener
    batch: Optional[Batch] = None
    prefetch: Optional[Prefetch] = None
import pika
import threading
import pika.channel
from typing import Callable, List, Dict, Optional, Type, Any, Union

import pika.exceptions
from .ConnectionManager import ConnectionManager
from .TopologyManager import TopologyManager, get_func_identifier
import pika.connection
from .models import T, F, Retry, DeadLetterQueue, Queue, ExchangeType, Exchange, Binding, Batch, Listener, Prefetch


class EasyAMQP:
    def __init__(self, 
                 connection_parameters: pika.ConnectionParameters | List[pika.ConnectionParameters], 
                 retry: Optional[Retry] = None,
                 on_connection_open: Optional[Callable[[pika.connection.Connection], None]]= None,
                 on_connection_error: Optional[Callable[[pika.connection.Connection, Union[str, Exception]], None]] = None,
                 on_channel_closed: Optional[Callable[[pika.channel.Channel, pika.exceptions.ChannelClosed], None]] = None
        ) -> None:        
        self._topology_manager = TopologyManager()
        self._connection_manager = ConnectionManager(
            params=connection_parameters,
            topology_manager=self._topology_manager,
            retry=retry,
            on_open=on_connection_open,
            on_error=on_connection_error,
            on_channel_closed=on_channel_closed
        )


    def declare_queue(self, queue: str, passive: bool = False, durable: bool = False, exclusive: bool = False, auto_delete: bool = False, arguments: Optional[Dict[str, Any]] = None, on_queue_declared: Optional[Callable[[pika.channel.Channel, 'Queue'], None]] = None) -> Callable[[F], F]:
        def decorator(func: F) -> F:
            self._topology_manager.add_queue(get_func_identifier(func), Queue(
                name=queue,
                passive=passive,
                durable=durable,
                exclusive=exclusive,
                auto_delete=auto_delete,
                arguments=arguments,
                dead_letter_queue=None,
                on_queue_declared=on_queue_declared
            ))
            return func
        return decorator

    def declare_exchange(self, exchange: str, exchange_type: ExchangeType = ExchangeType.direct, passive: bool = False, durable: bool = False, auto_delete: bool = False, internal: bool = False, arguments: Optional[Dict[str, Any]] = None, on_exchange_declared: Optional[Callable[[pika.channel.Channel, 'Exchange'], None]] = None) -> Callable[[F], F]:
        def decorator(func: F) -> F:
            self._topology_manager.add_exchange(get_func_identifier(func), Exchange(
                name=exchange,
                type=exchange_type,
                passive=passive,
                auto_delete=auto_delete,
                durable=durable,
                arguments=arguments,
                internal=internal,
                on_exchange_declared=on_exchange_declared
            ))
            return func
        return decorator

    def bind(self, exchange:str, queue: str, routing_key: str, arguments: Optional[Dict[str, Any]] = None, on_binding_declared: Optional[Callable[[pika.channel.Channel, 'Binding'], None]] = None) -> Callable[[F], F]:
        def decorator(func: F) -> F:
            self._topology_manager.add_binding(Binding(
                exchange=exchange,
                queue=queue,
                routing_key=routing_key,
                arguments=arguments,
                on_binding_declared=on_binding_declared
            ))
            return func
        return decorator

    def prefetch(self, prefetch_count: int = 0, prefetch_size: int = 0, global_qos: bool = False) -> Callable[[F], F]:
        def decorator(func: F) -> F:
            self._topology_manager.add_prefetch(get_func_identifier(func), Prefetch(
                    count=prefetch_count,
                    size=prefetch_size,
                    global_qos=global_qos
            ))
            return func
        return decorator
    
    def dead_letter(self, x_dead_letter_exchange: str, x_dead_letter_routing_key: str,  x_max_length: Optional[int] = None, x_message_ttl:  Optional[int] = None) -> Callable[[F], F]:
        def decorator(func: F) -> F:
            self._topology_manager.add_dead_letter(get_func_identifier(func), DeadLetterQueue(
                x_dead_letter_exchange=x_dead_letter_exchange,
                x_dead_letter_routing_key=x_dead_letter_routing_key,
                x_max_length=x_max_length,
                x_message_ttl=x_message_ttl
            ))

            return func
        return decorator

    def batch(self, batch_time: float = 0.2) -> Callable[[F], F]:
        def decorator(func: F) -> F:
            self._topology_manager.add_batch_consumer(get_func_identifier(func), Batch(
                batch_time=batch_time,
                scheduled=False,
                items=[]
            ))
            return func
        return decorator
    
    def listen_batch(self, queue: str, message_type: Type[T], batch_time: float = 0.2, auto_ack: bool = True, exclusive: bool = False, consumer_tag: Optional[str] = None, arguments: Optional[Dict[str, Any]] = None, custom_parser: Optional[Callable[[bytes], T]] = None, on_channel_open: Optional[Callable[[pika.channel.Channel], None]] = None) -> Callable[[F], F]:
        def decorator(func: F) -> F:
            self._topology_manager.add_batch_consumer(get_func_identifier(func), Batch(
                batch_time=batch_time,
                scheduled=False,
                items=[]
            ))
            self._topology_manager.add_listener(get_func_identifier(func), Listener(
                    func=func,
                    queue=queue,
                    message_type=message_type,
                    auto_ack=auto_ack,
                    exclusive=exclusive,
                    consumer_tag=consumer_tag,
                    arguments=arguments,
                    parser=custom_parser,
                    on_channel_open=on_channel_open
            ))
            return func
        return decorator

    def listen(self, queue: str, message_type: Type[T], auto_ack: bool = True, exclusive: bool = False, consumer_tag: Optional[str] = None, arguments: Optional[Dict[str, Any]] = None, custom_parser: Optional[Callable[[bytes], T]] = None, on_channel_open: Optional[Callable[[pika.channel.Channel], None]] = None) -> Callable[[F], F]:
        def decorator(func: F) -> F: 
            self._topology_manager.add_listener(get_func_identifier(func), Listener(
                    func=func,
                    queue=queue,
                    message_type=message_type,
                    auto_ack=auto_ack,
                    exclusive=exclusive,
                    consumer_tag=consumer_tag,
                    arguments=arguments,
                    parser=custom_parser,
                    on_channel_open=on_channel_open
            ))
    
            return func
        return decorator


    def add_queue(self, queue: Queue) -> None:
        self._topology_manager.add_queue(queue.name, queue)
    
    def add_exchange(self, exchange: Exchange) -> None:
        self._topology_manager.add_exchange(exchange.name, exchange)

    def add_binding(self, binding: Binding) -> None:
        self._topology_manager.add_binding(binding)

    def run_in_thread(self) -> threading.Thread:
        return self._connection_manager.run_in_thread()

    def run(self) -> None:
        self._connection_manager.start()

    def stop(self) -> None:
        self._connection_manager.close() 


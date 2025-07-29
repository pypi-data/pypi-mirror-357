import pika.connection
from .TopologyManager import TopologyManager
import pika.channel
from typing import Callable, Any
from .logger import LOGGER
import pika
from functools import partial
from .models import Queue, Exchange, Binding


class Declarator:
    def __init__(self, connection: pika.connection.Connection, channel: pika.channel.Channel, topology_manager: TopologyManager, on_finish: Callable[[pika.connection.Connection, pika.channel.Channel], None]) -> None:
        self._connection = connection
        self._channel = channel
        self._topology_manager = topology_manager
        self._on_finish = on_finish
        declarations =  len(self._topology_manager.queues()) + len(self._topology_manager.exchanges()) + len(self._topology_manager.bindings())
        self._remaining = declarations
        self._count_declarations = declarations


    def declare(self):
        if self._remaining == 0:
            LOGGER.debug("No declarations to perform, moving on..")
            self._on_finish(self._connection, self._channel)
            return
        
        self._declare_queues()
        self._declare_exchanges()
        self._apply_bindings()

    def _task_done(self, callable_fn: Callable[[], None], _: Any = None) -> None:
        self._remaining -= 1
        LOGGER.debug(f"declaration task done, remaining: {self._remaining} of {self._count_declarations}")
        callable_fn()
        
        if self._remaining == 0:
            self._on_finish(self._connection, self._channel)

    def _declare_queues(self):
        for queue in self._topology_manager.queues():
            LOGGER.debug(f"declare queue: {queue.name}")
            args = (queue.arguments or {}).copy()
            if queue.dead_letter_queue:
                args.update(queue.dead_letter_queue.to_args())

            def make_callback_fn(queue_snapshot: Queue) -> Callable[[], None]:
                def callback() -> None:
                    LOGGER.debug(f"queue: {queue_snapshot.name} is declared")
                    if queue_snapshot.on_queue_declared:
                        queue_snapshot.on_queue_declared(self._channel, queue_snapshot)
                return callback
            callback_fn = make_callback_fn(queue)
            self._channel.queue_declare(
                queue=queue.name,
                passive=queue.passive,
                durable=queue.durable,
                exclusive=queue.exclusive,
                auto_delete=queue.auto_delete,
                arguments=args,
                callback=partial(self._task_done, callback_fn)
            )



    def _declare_exchanges(self):
        for exchange in self._topology_manager.exchanges():
            LOGGER.debug(f"declare exchange: {exchange.name}")


            def make_callback_fn(exchange_snapshot: Exchange) -> Callable[[], None]:
                def callback() -> None:
                    LOGGER.debug(f"{exchange_snapshot.name} is declared")
                    if exchange_snapshot.on_exchange_declared:
                        exchange_snapshot.on_exchange_declared(self._channel, exchange_snapshot)
                return callback
            
            callback_fn = make_callback_fn(exchange)

            self._channel.exchange_declare(
                exchange=exchange.name,
                exchange_type=exchange.type.value,
                passive=exchange.passive,
                durable=exchange.durable,
                auto_delete=exchange.auto_delete,
                internal=exchange.internal,
                arguments=exchange.arguments,
                callback=partial(self._task_done, callback_fn)
            )
    
    def _apply_bindings(self) -> None:
        for binding_config in self._topology_manager.bindings():
            LOGGER.debug(f"bind queue: {binding_config.queue} an exchange: {binding_config.exchange} with routingkey: {binding_config.routing_key}")
            def make_callback_fn(binding_snapshot: Binding) -> Callable[[], None]:
                def callback() -> None:
                    LOGGER.debug( f"bind queue: {binding_snapshot.queue} an exchange: {binding_snapshot.exchange} with routingkey: {binding_snapshot.routing_key} binded")
                return callback
            callback_fn = make_callback_fn(binding_config)

            self._channel.queue_bind(
                exchange=binding_config.exchange, queue=binding_config.queue,
                routing_key=binding_config.routing_key, arguments=binding_config.arguments,
                callback=partial(self._task_done, callback_fn)
            )
from typing import Callable, List, Dict, Any
from .models import DeadLetterQueue, Queue, Exchange, Binding, Batch, Listener, Prefetch, Handler
from .logger import LOGGER

def get_func_identifier(func: Callable[..., Any]) -> str:
    return f"{func.__module__}.{func.__qualname__}"

class TopologyManager:
    def __init__(self) -> None:
        self._listener: Dict[str, Listener] = {}
        self._prefetch: Dict[str, Prefetch] = {}
        self._batch: Dict[str, Batch] = {}
        self._queues_to_declare: Dict[str, Queue] = {}
        self._exchanges_to_declare: Dict[str, Exchange] = {}
        self._dead_letter_queues: Dict[str, DeadLetterQueue] = {}
        self._bindings: List[Binding] = []


    def add_queue(self, caller_name: str, queue: Queue) -> None:
        for func_name, queue_to_declare in self._queues_to_declare.items():
            if queue.name == queue_to_declare.name:
                LOGGER.warning(f"queue: {queue.name} is already declared in {func_name}, skipping")
                raise ValueError(f"queue: {queue} is already declared in {func_name}")
        if caller_name in self._dead_letter_queues:
            queue.dead_letter_queue = self._dead_letter_queues[caller_name]
        self._queues_to_declare[caller_name] = queue
        
    
    def add_exchange(self, caller_name: str, exchange: Exchange) -> None:
        for func_name, exchange_to_declare in self._exchanges_to_declare.items():
            if exchange.name == exchange_to_declare.name:
                LOGGER.warning(f"Exchange: {exchange} is already declared in {func_name}")
                raise ValueError(f"Exchange: {exchange} is already declared in {func_name}")
        self._exchanges_to_declare[caller_name] = exchange

    def add_binding(self, binding: Binding) -> None:
        self._bindings.append(binding)

    def add_prefetch(self, caller_name: str, prefetch: Prefetch) -> None:
        self._prefetch[caller_name] = prefetch

    def add_dead_letter(self, caller_name: str, dlq: DeadLetterQueue) -> None:
        self._dead_letter_queues[caller_name] = dlq

    def add_batch_consumer(self, caller_name: str, batch: Batch) -> None:
        self._batch[caller_name] = batch

    def add_listener(self, caller_name: str, listener: Listener) -> None:
        self._listener[caller_name] = listener

    def handlers(self) -> List[Handler]:
        return [Handler(
            listener=listener,
            prefetch=self._prefetch[key] if key in self._prefetch else None,
            batch=self._batch[key] if key in self._batch else None
        )        
        for key, listener in self._listener.items()]
    
    def queues(self) -> List[Queue]:
        for key, queue in self._queues_to_declare.items():
            if key in self._dead_letter_queues:
                queue.dead_letter_queue = self._dead_letter_queues[key]
                
        return list(self._queues_to_declare.values())
    
    def bindings(self) -> List[Binding]:
        return self._bindings

    def exchanges(self) -> List[Exchange]:
        return list(self._exchanges_to_declare.values())
    

   
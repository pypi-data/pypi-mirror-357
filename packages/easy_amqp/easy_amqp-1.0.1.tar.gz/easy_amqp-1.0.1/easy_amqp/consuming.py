import pika
import pika.channel
import pika.spec
from typing import List
from .models import Message, Handler
from . import parser
from .logger import LOGGER

def start_consuming(handler: Handler, channel: pika.channel.Channel):
    listener = handler.listener
    LOGGER.debug(f"Setting up consumer for queue {listener.queue} on channel {channel.channel_number}")
    if listener.on_channel_open:
        listener.on_channel_open(channel)
    if handler.prefetch:
        pf = handler.prefetch
        channel.basic_qos(
            prefetch_count=pf.count,
            prefetch_size=pf.size,
            global_qos=pf.global_qos
        )
    channel.basic_consume(
        queue=listener.queue,
        on_message_callback=lambda ch, method, props, body: dispatch(handler, ch, method, props, body),
        auto_ack=listener.auto_ack,
        exclusive=listener.exclusive,
        consumer_tag=listener.consumer_tag,
        arguments=listener.arguments
    )

def dispatch(handler: Handler, channel: pika.channel.Channel,
                method: pika.spec.Basic.Deliver, props: pika.spec.BasicProperties, body: bytes) -> None:
    if handler.listener.parser:
        parsed_body = handler.listener.parser(body)
    else:
        parsed_body = parser.default_parser(body, handler.listener.message_type)
    msg = Message(body=parsed_body, method=method, props=props)

    if handler.batch:
        batch = handler.batch
        batch.items.append(msg)
        if not batch.scheduled:
            batch.scheduled = True
            channel.connection.ioloop.call_later( # type: ignore
                batch.batch_time,
                lambda: _deliver_batch(handler, channel)
            )
    else:
        _callback(handler, msg, channel)

def _deliver_batch(handler: Handler, channel: pika.channel.Channel):
    batch = handler.batch
    assert batch is not None
    items, batch.items = batch.items, []
    batch.scheduled = False
    _callback(handler, items, channel)



def _callback(handler: Handler, message: Message | List[Message], channel: pika.channel.Channel):
    handler.listener.func(message, channel)
import pika
import threading
import pika.channel
from typing import Callable, List, Optional,Union
import time

import pika.exceptions
from .TopologyManager import TopologyManager
from .models import Retry
import pika.connection
from . import consuming
from .logger import LOGGER
from .Declarator import Declarator
from functools import partial



class ConnectionManager:
    def __init__(self,
                 params: Union[pika.ConnectionParameters, List[pika.ConnectionParameters]],
                 topology_manager: TopologyManager,
                 retry: Optional[Retry] = None,
                 on_open: Optional[Callable[[pika.connection.Connection], None]] = None,
                 on_error: Optional[Callable[[pika.connection.Connection, Union[str, Exception]], None]] = None,
                 on_channel_closed: Optional[Callable[[pika.channel.Channel, pika.exceptions.ChannelClosed], None]] = None):
        self._params = params
        self._topology_manager = topology_manager
        self._retry = retry
        self._custom_on_open = on_open
        self._custom_on_error = on_error
        self._custom_on_channel_closed = on_channel_closed
        self._connection: Optional[pika.SelectConnection] = None
        self._ioloop_thread: Optional[threading.Thread] = None
        self._last_used_index = -1

        self._connection_closed = False

    def _choose_params(self) -> pika.ConnectionParameters:
        if isinstance(self._params, list):
            if len(self._params) == 1:
                return self._params[0]
            if self._last_used_index != -1:
                self._last_used_index = (self._last_used_index + 1) % len(self._params)
            else:
                self._last_used_index = 0
            return self._params[self._last_used_index]
        return self._params

    def _connect(self) -> pika.SelectConnection:
        return pika.SelectConnection(
            parameters=self._choose_params(),
            on_open_callback=self._on_open,
            on_open_error_callback=self._on_error_callback
        )

    def _on_open(self, conn: pika.connection.Connection):
        LOGGER.debug("Connection opened")
       
        if self._custom_on_open:
            self._custom_on_open(conn)
        conn.channel(on_open_callback=partial(self._on_channel_open_declare, conn))
      

    def _on_declaration_finish(self, conn: pika.connection.Connection, declaration_channel: pika.channel.Channel) -> None:
        if self._connection_closed:
            LOGGER.debug("connection is already closed, cannot proceed with finish declaration")
            return
        LOGGER.debug("All declarations finished, starting consumers")
        declaration_channel.close()  # type: ignore
        for handler in self._topology_manager.handlers():
            channel = conn.channel(on_open_callback=lambda ch, h=handler: consuming.start_consuming(h, ch))
            channel.add_on_close_callback(self._on_channel_closed)    # type: ignore   


    def _on_channel_closed(self, channel: pika.channel.Channel, exception: pika.exceptions.ChannelClosed):
        if self._connection_closed:
            LOGGER.debug(f"cannot close channel because, connection is already closed, reason for channel close: {str(exception)}")
            return

        LOGGER.debug(f"Channel {channel.channel_number}, reason: {str(exception)}")
        if self._custom_on_channel_closed:
            self._custom_on_channel_closed(channel, exception)
        
        # channel is not closed by code
        if not isinstance(exception, pika.exceptions.ChannelClosedByClient):
            LOGGER.warning(f"Channel {channel.channel_number} not closed by broker: {str(exception)}")
            self.close()



    def _on_channel_open_declare(self, conn: pika.connection.Connection, channel: pika.channel.Channel) -> None:
        try:
            LOGGER.debug(f"channel open for declaration channel number: {channel.channel_number}")
            channel.add_on_close_callback(self._on_channel_closed)  # type: ignore
            declarator = Declarator(conn, channel, self._topology_manager, self._on_declaration_finish)
            declarator.declare()
        except:
            LOGGER.exception("Error during channel declaration")
            self.close()
            raise

    def _on_error_callback(self, conn: pika.connection.Connection, err: Union[str, Exception]):
        LOGGER.error(f"Connection error: {err}")
        if self._custom_on_error:
            self._custom_on_error(conn, err)
        raise ConnectionError("Unable to establish connection")

    def start(self):
        attempts = 0
        while True:
            try:
                self._connection = self._connect()
                self._connection.ioloop.start() # type: ignore       
                break
            except Exception as e:
                if not self._retry:
                    self.close()
                    raise e
                
                attempts += 1
                LOGGER.info(f"Reconnect attempt #{attempts} waiting: {self._retry.delay} second(s)")
                if self._retry.retries == -1:
                    time.sleep(self._retry.delay)
                    continue
                if attempts >= self._retry.retries:
                    LOGGER.error("Max retries reached, exiting.")
                    self.close()
                    raise e
               
                time.sleep(self._retry.delay)

    def run_in_thread(self) -> threading.Thread:
        self.ioloop_thread = threading.Thread(target=self.start, daemon=True)
        self.ioloop_thread.start()
        return self.ioloop_thread
    
    def close(self) -> None:
        if self._connection_closed:
            LOGGER.debug("Connection already closed")
            return
        if self._connection and not self._connection.is_closed:
            self._connection.close()
        if self._connection and self._connection.ioloop: # type: ignore
            self._connection.ioloop.stop() # type: ignore
        if hasattr(self, "_ioloop_thread") and self._ioloop_thread:
             self._ioloop_thread.join()
        self._connection_closed = True
        LOGGER.debug("connection closed and IOLoop stopped")

    def get_connection(self) -> pika.SelectConnection:
        if self._connection is None:
            raise ValueError("no connection is open")
        return self._connection
from typing import Type
from .models import T

from .logger import LOGGER
import json


def default_parser(body: bytes, message_type: Type[T]) -> T:
    if message_type is bytes:
        return body # type: ignore
    elif message_type is str:
        return body.decode('utf-8') # type: ignore
    elif message_type in (int, float, bool):
        parsed_json = json.loads(body)
        return message_type(parsed_json) # type: ignore
    else:
        try:
            data = json.loads(body)
            return message_type(**data)
        except (json.JSONDecodeError, TypeError) as e:
            try: 
                data = json.loads(body)
                return message_type(data) # type: ignore
            except (json.JSONDecodeError, TypeError) as exp:
                LOGGER.debug(f"Unable to parse message to typ {message_type}: {e}")
                raise ValueError(f"Unable to parse message to typ {message_type}: {e}") from exp
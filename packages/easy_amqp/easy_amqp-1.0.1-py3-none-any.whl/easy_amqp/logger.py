import logging

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(level=logging.DEBUG)

handler = logging.StreamHandler()
formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)

LOGGER.addHandler(handler)
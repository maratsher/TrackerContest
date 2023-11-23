import sys
import logging

from typing import Dict, Callable

_logger = logging.getLogger("Bus")
_logger.setLevel(logging.DEBUG)

_handler = logging.StreamHandler(stream=sys.stdout)
_handler.setFormatter(logging.Formatter(fmt='[%(name)s | %(threadName)s | %(asctime)s] %(message)s'))
_logger.addHandler(_handler)


class EventAlreadyExists(Exception):
    pass


class EventNotExist(Exception):
    pass


class Bus:

    __instance = None

    @staticmethod
    def instance():
        if Bus.__instance is None:
            Bus()
        return Bus.__instance

    def __init__(self):
        if Bus.__instance is not None and Bus.__instance is not self:
            raise Exception("Bus already exists!")
        else:
            Bus.__instance = self

        self.subscribers: Dict[str, Callable] = dict()

    @staticmethod
    def subscribe(event_name: str, callback: Callable):
        bus = Bus.instance()

        if event_name not in bus.subscribers:
            bus.subscribers[event_name] = callback
            #_logger.debug(f"Added listener to {event_name} event")
        else:
            raise EventAlreadyExists(f"Event {event_name} already exist")

    @staticmethod
    def publish(event_name: str, *args, **kwargs):
        bus = Bus.instance()

        if event_name in bus.subscribers:
            #_logger.debug(f"Emit event {event_name}")
            if callable(bus.subscribers[event_name]):
                res = bus.subscribers[event_name](*args, **kwargs)
                return res
            else:
                return bus.subscribers[event_name]

        else:
            EventNotExist(f"Even {event_name} not exist")
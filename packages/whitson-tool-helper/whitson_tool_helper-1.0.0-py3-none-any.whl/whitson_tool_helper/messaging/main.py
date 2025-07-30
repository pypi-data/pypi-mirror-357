import sys
from enum import Enum
from typing import Callable, List

from pika.exceptions import ChannelClosedByBroker
from whitson_tool_helper.logger import LOGGER


class MessagingSystem(Enum):
    pubsub = "pubsub"
    rabbitmq = "rabbitmq"


class ConsumerService(Enum):
    listener = "listener"
    uploader = "uploader"


class MessagingSystemNotSupportedError(Exception):
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f"Messaging system {self.name} not supported at the moment"


class Consumer:
    def __init__(
        self,
        messaging_system: MessagingSystem,
        process_function: Callable,
        service: ConsumerService = ConsumerService.listener,
    ):
        if messaging_system == MessagingSystem.pubsub:
            from whitson_tool_helper.messaging import pubsub

            self._consumer = pubsub.PubsubConsumer(process_function)
        elif messaging_system == MessagingSystem.rabbitmq:
            from whitson_tool_helper.messaging import rabbitmq

            self._consumer = rabbitmq.RabbitMQConsumer(process_function, service.value)
        else:
            raise MessagingSystemNotSupportedError(messaging_system)

        self._messaging_system = messaging_system

    def work(self):
        while True:
            LOGGER.info("Connecting to server...")
            try:
                self._consumer.work()
            except KeyboardInterrupt:
                LOGGER.info("Keyboard interrupt!")
                LOGGER.info("Consumer shut down!")
                sys.exit()
            except ChannelClosedByBroker as e:
                LOGGER.error("-- RABBITMQ ACCESS REFUSED --")
                LOGGER.error(e)
                sys.exit()
            except Exception as e:
                LOGGER.error("-- UNKNOWN ERROR ENCOUNTERED --")
                LOGGER.error(e)
            finally:
                if self._messaging_system == MessagingSystem.rabbitmq:
                    self._consumer.ack_and_close_connection()
                LOGGER.warning("Restarting worker")


class Publisher:
    def __init__(self, messaging_system: MessagingSystem, exchange: str = None):
        if messaging_system == MessagingSystem.pubsub:
            from whitson_tool_helper.messaging import pubsub

            self._consumer = pubsub.PubsubPublisher()
        elif messaging_system == MessagingSystem.rabbitmq:
            from whitson_tool_helper.messaging import rabbitmq

            self._consumer = rabbitmq.RabbitMQPublisher(exchange)
        else:
            raise MessagingSystemNotSupportedError(messaging_system)

    def publish(self, topic: str, payload: dict, meta_data: dict = {}, **kwargs):
        self._consumer.publish(topic, payload, meta_data, **kwargs)

    def publish_many(self, topic: str, payloads: List[dict], **kwargs):
        self._consumer.publish_many(topic, payloads, **kwargs)


class Mover:
    def __init__(self, messaging_system: MessagingSystem):
        if messaging_system == MessagingSystem.rabbitmq:
            from whitson_tool_helper.messaging import rabbitmq

            self._mover = rabbitmq.RabbitMQMover()
        else:
            raise MessagingSystemNotSupportedError(messaging_system)

    def move(self, number_of_messages: int, source: str, destination: str):
        self._mover.move(number_of_messages, source, destination)
